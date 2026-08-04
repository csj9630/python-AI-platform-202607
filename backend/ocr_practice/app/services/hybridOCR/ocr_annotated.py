"""

전체 흐름을 코드별 주석으로 해설해서 파일에 담았어. 핵심 흐름은 이래:

1. **`POST /jobs`** — 이미지/PDF 업로드, 검증(용량·매직바이트·암호PDF 등), Job 생성 후 즉시 201 응답. 실제 OCR은 `background_tasks`로 넘김.
2. **`process_all_job_models`** — 백그라운드 진입점. 파일을 페이지 단위로 **한 번만** 전처리(`prepare_document_pages`)한 뒤, 그 결과를 모든 지원 모델이 재사용하며 `asyncio.gather`로 동시 실행 → 렌더링 비용을 모델 수만큼 반복 안 함.
3. **`process_model_in_background`** — 모델 1개 OCR 실행(`to_thread`로 블로킹 작업을 스레드로 위임) 후 결과를 새 DB 세션으로 저장. 한 모델 실패가 다른 모델에 영향 안 주도록 예외를 여기서 흡수.
4. **`prepare_document_pages` / `recognize_document_pages`** — PDF는 `fitz`로 페이지별 2배 확대 렌더링 후 RGB→BGR 변환, 다중 페이지 결과는 텍스트/신뢰도/소요시간을 병합.
5. **`GET /jobs/{id}`** — 폴링용 상태 조회, 소유자 검증으로 404 은닉.
6. **`POST /jobs/{id}/models/{model}`** — 특정 모델만 동기적으로 즉시 재실행(응답까지 블로킹).
7. **`/translate`** — 실제 번역 엔진 미연동, 고정 텍스트 반환하는 **Mock API**(`is_mock: True`로 명시).
8. **`/correct`** — 로컬 Ollama LLM에 프롬프트를 보내 OCR 오탈자만 교정(사실·숫자·순서 변경 금지 지시).

특히 주목할 부분은 **DB 세션/트랜잭션 관리**야. `await session.rollback()`을 OCR처럼 오래 걸리는 작업 직전에 호출해서 커넥션 풀에 반납하고, 작업이 끝난 뒤엔 새 세션(`AsyncSessionLocal()`)으로 짧게 저장만 하는 패턴이 여러 곳에서 반복돼 — 커넥션 풀 고갈을 막기 위한 설계로 보여.
=====================================================================================
 [전체 흐름 요약]
 이 파일은 FastAPI 라우터로, "문서 업로드 → 여러 OCR 모델로 비동기 인식 → 결과 조회 →
 (선택) 번역/교정" 흐름을 담당하는 백엔드 서비스입니다.

 1) POST /jobs                      : 이미지/PDF 업로드 → OCR Job 생성 → 백그라운드에서
                                       모든 지원 모델을 동시에 실행
 2) GET  /jobs/{document_id}        : Job의 전체 상태 및 모델별 결과 조회
 3) POST /jobs/{id}/models/{model}  : 특정 모델 하나만 즉시(동기 요청-응답) 재실행
 4) POST /translate                 : (Mock) 번역 API - 실제 번역 엔진 미연동, 고정 텍스트 반환
 5) POST /correct                   : 로컬 Ollama LLM을 이용한 OCR 오탈자 교정
=====================================================================================
"""

from asyncio import gather, to_thread
import csv
from io import StringIO
import json
import logging
from pathlib import Path
import fitz  # PyMuPDF: PDF 파싱 및 페이지 -> 이미지 렌더링에 사용
import httpx  # Ollama(로컬 LLM 서버) 호출용 비동기 HTTP 클라이언트
import numpy as np
from pydantic import BaseModel

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.core.dependencies import CurrentUser, DatabaseSession
from app.core.database import AsyncSessionLocal
from app.core.config import get_settings
from app.services.ocr_engines import OCRResult, SUPPORTED_MODELS, configure_web_engines, recognize_preprocessed
from app.services.ocr_jobs import create_ocr_job, get_owned_ocr_job, save_model_result
from ocr_pipeline import OCRPipeline, OCRPipelineConfig

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
# 모듈 로드 시점(서버 기동 시 1회)에 웹 기반 OCR 엔진(예: 브라우저/외부 API 기반 엔진)을
# 초기화합니다. 요청마다 초기화 비용을 지불하지 않기 위해 전역에서 한 번만 실행됩니다.
configure_web_engines()


class TranslationRequest(BaseModel):
    """POST /translate 요청 바디: 번역할 텍스트 + 목표 언어 코드(en/ko/ja/zh 등)"""
    text: str
    target_language: str


class CorrectionRequest(BaseModel):
    """POST /correct 요청 바디: OCR로 추출된 원문 텍스트"""
    text: str


def normalize_ground_truth(filename: str, content: str) -> str:
    """
    채점/평가용 정답(ground truth) 파일을 순수 텍스트로 정규화합니다.
    - .json : 중첩된 dict/list를 재귀적으로 순회하며 모든 leaf 값을 문자열로 모아 줄바꿈으로 join
    - .csv  : 각 행(row)의 셀들을 공백으로 이어 붙이고, 행 사이는 줄바꿈으로 구분
    - 그 외(.txt 등) : 원본 내용을 그대로 반환
    OCR 결과와 정답을 같은 "순수 텍스트" 형태로 비교하기 위한 전처리 단계입니다.
    """
    suffix = Path(filename).suffix.lower()
    if suffix == ".json":
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            # 정답 JSON이 깨져 있으면 업로드 단계에서 바로 400 반환 (조용히 무시하지 않음)
            raise HTTPException(status_code=400, detail="정답 JSON 형식이 올바르지 않습니다.") from exc

        values: list[str] = []

        def collect(value):
            # dict/list를 재귀적으로 파고들어 스칼라 값만 문자열로 수집하는 헬퍼
            if isinstance(value, dict):
                for nested in value.values():
                    collect(nested)
            elif isinstance(value, list):
                for nested in value:
                    collect(nested)
            elif value is not None:
                values.append(str(value))
        collect(payload)
        return "\n".join(values)
    if suffix == ".csv":
        # csv.reader로 행을 파싱한 뒤, 각 셀의 앞뒤 공백을 제거하고 공백으로 합침
        return "\n".join(" ".join(cell.strip() for cell in row) for row in csv.reader(StringIO(content)))
    return content


# 이미지나 PDF 파일, 그리고 선택적으로 정답 파일을 업로드 받아 새로운 OCR 작업을 생성하는 엔드포인트입니다
@router.post("/jobs", status_code=201)
async def create_job(
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    session: DatabaseSession,
    file: UploadFile = File(...),
    ground_truth: UploadFile | None = File(None),
):
    """
    [1단계: 업로드 & 검증]
    이미지 또는 PDF 파일을 업로드받아 OCR Job을 생성하고,
    실제 OCR 처리는 백그라운드 태스크로 넘겨서 즉시 응답(201)합니다.
    """
    # 경로 조작(path traversal) 방지를 위해 Path(...).name으로 순수 파일명만 추출
    safe_name = Path(file.filename or "uploaded-image").name
    is_pdf = file.content_type == "application/pdf" or Path(safe_name).suffix.lower() == ".pdf"

    # content-type이 없거나, image/* 도 아니고 PDF도 아니면 거부
    if not file.content_type or (not file.content_type.startswith("image/") and not is_pdf):
        raise HTTPException(status_code=400, detail="이미지 또는 PDF 파일만 업로드할 수 있습니다.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="비어 있는 파일입니다.")
    if len(contents) > 10 * 1024 * 1024:
        # 10MB 초과 시 413 Payload Too Large
        raise HTTPException(status_code=413, detail="파일 크기는 10MB 이하여야 합니다.")

    if is_pdf:
        # 매직 바이트(%PDF-) 검사로 확장자만 바꾼 위장 파일을 1차 필터링
        if not contents.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="올바른 PDF 파일이 아닙니다.")
        try:
            # fitz로 실제 열어보며 2차 검증: 암호 여부, 페이지 존재 여부 확인
            with fitz.open(stream=contents, filetype="pdf") as pdf:
                if pdf.needs_pass:
                    raise HTTPException(status_code=400, detail="암호가 설정된 PDF는 업로드할 수 없습니다.")
                if pdf.page_count == 0:
                    raise HTTPException(status_code=400, detail="페이지가 없는 PDF입니다.")
        except HTTPException:
            # 위에서 의도적으로 던진 HTTPException은 그대로 재전파
            raise
        except (fitz.FileDataError, RuntimeError) as exc:
            # fitz가 파싱 중 던지는 손상 파일 관련 예외는 400으로 변환
            raise HTTPException(status_code=400, detail="손상되었거나 읽을 수 없는 PDF입니다.") from exc

    # 정답(ground truth) 파일은 선택 사항. 있으면 크기 제한 및 인코딩 검증 후 정규화
    truth_name = None
    truth_content = None
    if ground_truth is not None:
        truth_name = Path(ground_truth.filename or "ground-truth.txt").name
        truth_bytes = await ground_truth.read()
        if len(truth_bytes) > 2 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="정답 데이터는 2MB 이하여야 합니다.")
        try:
            # utf-8-sig: BOM이 붙은 UTF-8 파일도 안전하게 디코딩
            truth_content = normalize_ground_truth(
                truth_name,
                truth_bytes.decode("utf-8-sig"),
            )
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="정답 데이터는 UTF-8 텍스트여야 합니다.") from exc

    # DB에 Job 레코드 생성 (원본 파일, 정답 데이터까지 함께 저장)
    document = await create_ocr_job(
        session,
        user_id=current_user.user_id,
        original_name=safe_name,
        content_type=file.content_type,
        image_bytes=contents,
        ground_truth_filename=truth_name,
        ground_truth_content=truth_content,
    )
    document_id = document.document_id
    owner_id = current_user.user_id

    # [중요] FastAPI의 BackgroundTasks는 응답이 클라이언트로 전송된 "직후"에 실행되지만,
    # 이 요청 트랜잭션의 커넥션/세션은 아직 살아있을 수 있습니다.
    # create_ocr_job 내부의 refresh() 등이 트랜잭션을 연 채로 남겨둘 수 있으므로,
    # 백그라운드 작업이 별도의 새 세션(AsyncSessionLocal)을 안전하게 얻을 수 있도록
    # 여기서 명시적으로 rollback()하여 커넥션을 커넥션 풀에 반납합니다.
    await session.rollback()

    # 실제 OCR 수행은 백그라운드로 위임 -> 사용자는 오래 기다리지 않고 즉시 201 응답을 받음
    background_tasks.add_task(process_all_job_models, document_id, owner_id)

    return {
        "document_id": document_id,
        "filename": safe_name,
        "ground_truth_filename": truth_name,
        "models": sorted(SUPPORTED_MODELS),  # 어떤 모델들이 백그라운드에서 돌고 있는지 안내
    }

# 모델 1개 OCR 실행 + 결과 저장
# 스레드 풀(to_thread)에서 실제 OCR 모델 추론을 수행한 뒤, 최종 텍스트와 신뢰도, 소요 시간 등의 결과를 DB에 업데이트(save_model_result)합니다
async def process_model_in_background(
    document_id: str,
    user_id: str,
    model_name: str,
    bundles,
) -> None:
    """
    [2단계: 모델 1개 실행 + 결과 저장]
    이미 전처리된 bundles(페이지별 이미지 데이터)를 받아 특정 모델로 OCR을 수행하고,
    성공/실패 여부와 무관하게 결과를 DB에 저장합니다.
    process_all_job_models에서 모델별로 병렬 호출됩니다.
    """
    try:
        # OCR 자체는 CPU/GPU 바운드 + 수 분이 걸릴 수 있는 블로킹 작업이므로
        # to_thread로 별도 스레드에서 실행하여 이벤트 루프를 막지 않음
        result = await to_thread(recognize_document_pages, model_name, bundles)
        raw_text, confidence = result.text, result.average_confidence
        elapsed_ms, error_message = round(result.total_elapsed_ms), result.error
        details = compact_result_details(result)
    except Exception as exc:
        # 개별 모델 실패가 전체 Job(다른 모델들)에 영향을 주지 않도록 여기서 흡수
        logger.exception("Background OCR failed: document=%s model=%s", document_id, model_name)
        raw_text = None
        confidence = None
        elapsed_ms, details = 0, None
        error_message = str(exc)

    # OCR 처리(수 분 소요 가능) 동안에는 DB 세션/트랜잭션을 절대 붙들고 있지 않고,
    # 결과가 나온 뒤에야 새 세션을 열어 짧게 커넥션을 사용하고 반납
    async with AsyncSessionLocal() as session:
        document = await get_owned_ocr_job(session, document_id, user_id)
        if document is None:
            # 그 사이 문서가 삭제되었거나 소유권이 바뀌었으면 조용히 종료
            return
        await save_model_result(
            session,
            document=document,
            model_name=model_name,
            raw_text=raw_text,
            confidence=confidence,
            elapsed_ms=elapsed_ms,
            error_message=error_message,
            details=details,
        )

# PDF는 fitz로 페이지별 2배 확대 렌더링 후 RGB→BGR 변환
def prepare_document_pages(path: Path) -> list:
    """Render every PDF page or load one image into reusable OCR bundles."""
    # 동기 함수 (to_thread로 스레드풀에서 실행됨). 이미지 로딩/디코딩 등 CPU 작업 포함.
    pipeline = OCRPipeline(OCRPipelineConfig())
    if path.suffix.lower() != ".pdf":
        # 단일 이미지 파일: 파이프라인의 표준 전처리(리사이즈/정규화 등) 1회 수행
        return [pipeline.prepare(path)]

    bundles = []
    with fitz.open(path) as pdf:
        for page in pdf:
            # 2배 확대 행렬로 렌더링 -> 해상도를 높여 OCR 인식률 향상
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            # raw pixel buffer(RGB, alpha 없음)를 (H, W, 3) numpy 배열로 재구성
            rgb = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, 3)
            # fitz는 RGB, OpenCV 계열 파이프라인은 보통 BGR을 기대하므로 채널 순서를 뒤집음(RGB->BGR)
            bundles.append(pipeline.prepare_image(rgb[:, :, ::-1].copy()))
    # PDF의 각 페이지를 이미지로 렌더링한 뒤 개별적으로 전처리하여 리스트로 반환
    return bundles

# 다중 페이지 결과는 텍스트/신뢰도/소요시간을 병합
def recognize_document_pages(model_name: str, bundles: list) -> OCRResult:
    """
    [핵심 인식 로직]
    페이지(=bundle) 단위로 recognize_preprocessed를 호출하고,
    여러 페이지(PDF)인 경우 결과를 하나의 OCRResult로 병합합니다.
    """
    page_results = [recognize_preprocessed(model_name, bundle) for bundle in bundles]

    if len(page_results) == 1:
        # 이미지 1장(또는 PDF 1페이지)이면 병합 없이 그대로 반환
        return page_results[0]

    # 여러 페이지 병합 로직:
    # - 신뢰도(confidence)는 값이 있는 페이지들의 단순 평균
    confidences = [result.average_confidence for result in page_results if result.average_confidence is not None]
    # - 에러는 "N페이지: 에러메시지" 형태로 페이지 번호를 붙여 모두 취합 (한 페이지 실패해도 나머지는 살림)
    errors = [f"{index + 1}페이지: {result.error}" for index, result in enumerate(page_results) if result.error]
    return OCRResult(
        model=model_name,
        # 각 페이지 텍스트를 빈 줄 두 개로 구분해 이어 붙임 (빈 텍스트인 페이지는 제외)
        text="\n\n".join(result.text for result in page_results if result.text),
        # 개별 인식 항목(바운딩박스 등)은 모든 페이지 것을 평탄화하여 합침
        items=[item for result in page_results for item in result.items],
        average_confidence=sum(confidences) / len(confidences) if confidences else None,
        preprocessing_variant="multi_page",
        # 전처리/추론/총 소요시간은 페이지별 합산
        preprocess_elapsed_ms=sum(result.preprocess_elapsed_ms for result in page_results),
        inference_elapsed_ms=sum(result.inference_elapsed_ms for result in page_results),
        total_elapsed_ms=sum(result.total_elapsed_ms for result in page_results),
        # 모델 초기화 시간은 페이지마다 반복되는 게 아니라 최초 1회 값이므로 첫 페이지 값을 사용
        initialization_elapsed_ms=page_results[0].initialization_elapsed_ms,
        error="; ".join(errors) if errors else None,
    )

# DB에 저장할 데이터 중 용량 크거나 중복 데이터 제외.
def compact_result_details(result: OCRResult) -> dict:
    """Keep timing/debug metadata without duplicating raw text and every OCR box."""
    # DB의 details 컬럼에는 타이밍/디버그 메타데이터만 저장하고,
    # 이미 raw_text 컬럼에 저장되는 본문(text)과 용량이 큰 개별 인식 박스(items)는 제외하여
    # 같은 데이터가 중복 저장되는 것을 방지
    details = result.to_dict()
    details.pop("text", None)
    details.pop("items", None)
    details["item_count"] = len(result.items)  # 개수 정보만 남겨 몇 개의 텍스트 블록이 인식됐는지 확인 가능
    return details

# 백그라운드 진입점. 파일을 페이지 단위로 한 번만 전처리
async def process_all_job_models(document_id: str, user_id: str) -> None:
    """
    [백그라운드 태스크 진입점]
    create_job에서 add_task로 등록되는 함수.
    1) 파일을 페이지 단위로 한 번만 전처리(prepare_document_pages)하고,
    2) 그 결과(bundles)를 모든 지원 모델이 재사용하도록 하여
    3) 모델별 OCR을 asyncio.gather로 동시에 실행합니다.
    -> 페이지 렌더링/전처리를 모델 수만큼 반복하지 않아 효율적입니다.
    """
    async with AsyncSessionLocal() as session:
        document = await get_owned_ocr_job(session, document_id, user_id)
        if document is None:
            return
        image_path = settings.storage_dir / document.file_path
        # 여기서 session은 with 블록을 벗어나며 자동으로 정리됨 (짧게만 사용)

    try:
        # 전처리(PDF 렌더링 등)도 블로킹 작업이므로 스레드풀에서 실행
        bundles = await to_thread(prepare_document_pages, image_path)
    except Exception as exc:
        # 전처리 자체가 실패하면(손상 파일 등) 모든 모델에 대해 동일한 에러를 기록해 두어
        # 클라이언트가 "일부 모델만 결과 없음"이 아니라 전체 실패를 명확히 알 수 있게 함
        logger.exception("OCR preprocessing failed: %s", document_id)
        async with AsyncSessionLocal() as session:
            document = await get_owned_ocr_job(session, document_id, user_id)
            if document:
                for name in sorted(SUPPORTED_MODELS):
                    await save_model_result(session, document=document, model_name=name, raw_text=None, confidence=None, elapsed_ms=0, error_message=f"이미지 전처리 실패: {exc}")
        return

    # 지원되는 모든 모델(SUPPORTED_MODELS)을 병렬(concurrent)로 실행.
    # asyncio.gather는 코루틴들을 동시에 스케줄링하며, 각 모델은 내부적으로 to_thread를 쓰므로
    # 실제로는 여러 스레드에서 동시에 OCR이 수행됨.
    await gather(*(
        process_model_in_background(document_id, user_id, model_name, bundles)
        for model_name in sorted(SUPPORTED_MODELS)
    ))

# 특정 문서 ID에 대한 작업 진행 상태와 각 OCR 모델들의 추출 결과, 메트릭스(CER/WER 등)를 클라이언트에게 반환합니다.
@router.get("/jobs/{document_id}")
async def get_job_status(
    document_id: str,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    """
    [3단계: 상태 조회]
    프론트엔드가 폴링(polling)하며 각 모델의 진행 상태/결과를 확인하는 용도로 사용.
    소유자 검증(get_owned_ocr_job)을 통해 다른 사용자의 Job은 조회할 수 없음(404로 은닉).
    """
    document = await get_owned_ocr_job(session, document_id, current_user.user_id)
    if document is None:
        raise HTTPException(status_code=404, detail="OCR 작업을 찾을 수 없습니다.")
    return {
        "document_id": document.document_id,
        "filename": document.original_name,
        "status": document.status,
        "models": [
            {
                "model_name": item.model_name,
                "extracted_text": item.raw_text,
                "confidence": item.confidence,
                "elapsed_ms": item.elapsed_ms,
                "metrics": item.metrics,
                "details": item.details,
                "status": item.status,
                "error_message": item.error_message,
            }
            # 모델 이름순 정렬로 항상 동일한 순서로 응답 (프론트에서 안정적으로 렌더링 가능)
            for item in sorted(document.ocr_model_results, key=lambda result: result.model_name)
        ],
    }

# 특정 OCR 모델만 다시 실행하고 싶을 때 사용하는 엔드포인트로, 즉시 전처리 및 추론을 수행하고 결과를 DB에 갱신하여 반환합니다
@router.post("/jobs/{document_id}/models/{model_name}")
async def process_job_model(
    document_id: str,
    model_name: str,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    """
    [단일 모델 재실행 - 동기 방식]
    create_job과 달리 백그라운드로 넘기지 않고, 요청-응답 사이클 안에서 직접 OCR을 수행하여
    결과를 즉시 반환합니다. (예: 사용자가 특정 모델 결과만 다시 시도하고 싶을 때 사용)
    """
    if model_name not in SUPPORTED_MODELS:
        raise HTTPException(status_code=404, detail="지원하지 않는 OCR 모델입니다.")
    document = await get_owned_ocr_job(session, document_id, current_user.user_id)
    if document is None:
        raise HTTPException(status_code=404, detail="OCR 작업을 찾을 수 없습니다.")

    image_path = settings.storage_dir / document.file_path
    # 여기서도 마찬가지로, 이후 오래 걸릴 OCR 작업 동안 트랜잭션/커넥션을 붙들지 않도록
    # 먼저 rollback으로 반납한 뒤 작업을 진행
    await session.rollback()
    try:
        bundles = await to_thread(prepare_document_pages, image_path)
        ocr_result = await to_thread(recognize_document_pages, model_name, bundles)
        raw_text, confidence = ocr_result.text, ocr_result.average_confidence
        elapsed_ms, error_message, details = round(ocr_result.total_elapsed_ms), ocr_result.error, compact_result_details(ocr_result)
    except Exception as exc:
        logger.exception("OCR model failed: document=%s model=%s", document_id, model_name)
        raw_text = None
        confidence = None
        elapsed_ms, details = 0, None
        error_message = str(exc)

    # rollback으로 세션이 재사용 가능한 상태가 되었으므로, 저장 전에 document를 다시 조회
    # (트랜잭션이 끊겼다가 다시 시작되는 지점이라 최신 상태를 다시 가져오는 것이 안전)
    document = await get_owned_ocr_job(session, document_id, current_user.user_id)
    if document is None:
        raise HTTPException(status_code=404, detail="OCR 작업을 찾을 수 없습니다.")
    result = await save_model_result(
        session,
        document=document,
        model_name=model_name,
        raw_text=raw_text,
        confidence=confidence,
        elapsed_ms=elapsed_ms,
        error_message=error_message,
        details=details,
    )
    if error_message:
        # 이 엔드포인트는 동기 요청이므로, 실패 시 결과는 DB에 남겨두되
        # 클라이언트에게는 503(일시적 서비스 불가)으로 즉시 실패를 알림
        raise HTTPException(status_code=503, detail=error_message)
    return {
        "document_id": document_id,
        "model_name": result.model_name,
        "extracted_text": result.raw_text,
        "confidence": result.confidence,
        "elapsed_ms": result.elapsed_ms,
        "metrics": result.metrics,
        "details": result.details,
        "status": result.status,
    }

# 실제 번역 엔진 미연동
@router.post("/translate")
async def translate_text(
    request: TranslationRequest,
    current_user: CurrentUser,
):
    """
    [Mock 번역 API]
    실제 번역 엔진과 연동되어 있지 않고, 언어별로 미리 정의된 고정 문자열을 반환합니다.
    응답의 is_mock: True 플래그로 프론트엔드가 "실제 번역이 아님"을 알 수 있도록 표시.
    (데모/개발 단계용으로 보이며, 운영 반영 전 실제 번역 API 연동이 필요해 보입니다.)
    """
    translations = {
        "en": (
            "[Test English Translation]\n\n"
            "Total amount: KRW 27,500\n"
            "VAT included: KRW 2,500"
        ),
        "ko": (
            "[한국어 테스트 번역]\n\n"
            "합계 금액: 27,500원\n"
            "포함된 부가세: 2,500원"
        ),
        "ja": (
            "[日本語テスト翻訳]\n\n"
            "合計金額：27,500ウォン\n"
            "付加価値税込み：2,500ウォン"
        ),
        "zh": (
            "[中文测试翻译]\n\n"
            "总金额：27,500韩元\n"
            "包含增值税：2,500韩元"
        ),
    }

    return {
        # 지원하지 않는 언어 코드가 오면 영어(en) 번역으로 폴백
        "translated_text": translations.get(
            request.target_language,
            translations["en"],
        ),
        "target_language": request.target_language,
        "is_mock": True,
    }

# 로컬 Ollama LLM에 프롬프트를 보내 OCR 오탈자만 교정(사실·숫자·순서 변경 금지 지시)
@router.post("/correct")
async def correct_ocr_text(
    request: CorrectionRequest,
    current_user: CurrentUser,
):
    """Correct OCR typos with a configured local Ollama model without using GT data."""
    # [OCR 후처리 교정] 로컬에 띄운 Ollama LLM 서버에 프롬프트를 보내
    # OCR로 생긴 오탈자/잘못 분리된 글자만 교정하고, 사실/숫자/고유명사/문단 순서는
    # 임의로 바꾸지 않도록 지시하는 프롬프트를 구성합니다.
    source_text = request.text.strip()
    if not source_text:
        raise HTTPException(status_code=400, detail="교정할 텍스트가 비어 있습니다.")
    prompt = (
        "다음은 OCR로 추출한 문서입니다. 문맥상 명백한 OCR 오탈자와 잘못 분리된 글자만 교정하세요. "
        "사실, 숫자, 고유명사, 문단 순서를 임의로 추가하거나 요약하지 마세요. "
        "설명 없이 교정된 전체 본문만 출력하세요.\n\n"
        f"{source_text}"
    )
    try:
        # settings.ollama_timeout_seconds: LLM 응답이 늦어질 수 있어 별도 타임아웃 설정
        async with httpx.AsyncClient(timeout=settings.ollama_timeout_seconds) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/generate",
                # stream=False: 스트리밍 없이 전체 응답을 한 번에 받음
                json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            corrected = response.json().get("response", "").strip()
    except (httpx.HTTPError, ValueError) as exc:
        # 연결 실패, 타임아웃, 4xx/5xx, JSON 파싱 실패(ValueError) 등을 모두 묶어
        # "AI 교정 서버 연결 불가"라는 사용자 친화적 메시지로 변환
        logger.warning("Ollama correction failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=503,
            detail="AI 교정 서버에 연결할 수 없습니다. Ollama 실행 및 모델 설치 상태를 확인해 주세요.",
        ) from exc
    if not corrected:
        # LLM이 빈 응답을 준 경우 502(Bad Gateway)로 상위 서버 오류를 표시
        raise HTTPException(status_code=502, detail="AI 교정 결과가 비어 있습니다.")
    return {"corrected_text": corrected, "model": settings.ollama_model}
