# 🚀 Python & AI LLM 실습 플랫폼 (python-AI-platform-202607)

이 프로젝트는 **Python의 핵심 활용법**과 **다양한 AI LLM(대형 언어 모델) 및 OCR 기술을 실습**하고 학습하기 위한 개발 워크스페이스입니다. FastAPI를 활용한 백엔드 API 서버 구축부터 로컬 LLM(Ollama), OpenAI API(Structured Outputs), OCR 3종 성능 비교(Tesseract, EasyOCR, PaddleOCR) 및 Gemini AI 요약 파이프라인까지 연동하는 실전 예제를 포함하고 있습니다.

---

## 📌 주요 학습 목표
1. **Python 백엔드 개발**: FastAPI와 Pydantic을 활용한 RESTful API 설계 및 표준 예외 처리.
2. **로컬 LLM (Ollama) 실습**: 오픈소스 모델(`gemma3:1b` 등)을 이용한 스트리밍 답변, CLI 챗봇 및 API 서비스 연동.
3. **상용 LLM (OpenAI GPT) 연동**: OpenAI SDK를 활용하여 출력 형식을 강제하는 **Structured Outputs** 구현 및 문서 요약 API 설계.
4. **OCR & LLM 복합 파이프라인**: 이미지 및 PDF 문서 내 텍스트를 추출하고, 다중 OCR 엔진의 성능을 비교 분석한 후, Gemini LLM을 통해 오타 보정 및 핵심 요약 수행.

---

## 📂 프로젝트 구조 (Directory Structure)

```text
python-AI-platform-202607/
├── backend/                   # Python 백엔드 및 AI 연동 실습 소스
│   ├── main.py                # FastAPI 진입점 (기본 RESTful API 연습용)
│   ├── requirements.txt       # 공통 백엔드 패키지 의존성 정의
│   │
│   ├── Ollama_practice/       # 로컬 LLM(Ollama) 실습 폴더
│   │   ├── 01_stream.py       # 실시간 스트리밍 대답 (CLI)
│   │   ├── 02_chatBot.py      # 대화 기록(Memory Context) 보존형 CLI 챗봇
│   │   └── 03_useFastAPI.py   # Ollama 연동 FastAPI 채팅 API (/chat)
│   │
│   ├── GPT_document_self/     # OpenAI GPT 활용 문서 요약 실습 폴더
│   │   ├── app/
│   │   │   ├── main.py        # API 엔드포인트 및 오류 핸들링
│   │   │   ├── schemas.py     # Pydantic 기반 구조화된 입출력 스키마
│   │   │   ├── prompts.py     # 시스템 및 요약 프롬프트 관리
│   │   │   └── services/
│   │   │       └── gpt_summary.py # OpenAI SDK 기반 Structured Outputs 구현
│   │   └── _실습_GPT문서AI작업.md
│   │
│   ├── ocr_practice/          # OCR 3종 벤치마크 및 Gemini 요약 실습 폴더
│   │   ├── main.py            # OCR 벤치마크 실행 진입 스크립트
│   │   ├── app/
│   │   │   └── services/
│   │   │       ├── ocr/       # Tesseract, EasyOCR, PaddleOCR 모듈
│   │   │       └── llm/       # Gemini API 요약 연동 모듈 (google-genai SDK 사용)
│   │   ├── ocr_result_report.txt # 벤치마크 수행 분석 결과 리포트 (생성 파일)
│   │   └── sample.jpg / sample.pdf # 테스트용 문서 샘플
│   │
│   ├── practice/              # 기본 Python 문법 및 FastAPI 모듈별 실습용 임시 디렉토리
│   └── module_32_self / module_34_self # FastAPI 예외 처리 및 확장 실습 폴더
│
└── frontend/                  # 프론트엔드 실습용 임시 디렉토리 (구축 예정)
```

---

## 🛠️ 개발 환경 설정 및 설치

### 1. 가상환경 구성 및 패키지 설치
각 실습 디렉토리별 또는 backend 통합 환경에서 필요한 패키지를 설치합니다.

```bash
# backend 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화 (Windows)
python -m venv .venv
.venv\Scripts\activate

# 기본 패키지 설치
pip install -r requirements.txt
```

### 2. OCR 실습 관련 시스템 의존성 (Tesseract 설치 필수)
`ocr_practice`에서 Tesseract OCR 엔진을 사용하려면 로컬 시스템에 Tesseract가 설치되어 있어야 하며, 시스템 환경 변수(PATH)에 등록되어 있어야 합니다.

### 3. 환경 변수(`.env`) 설정
OpenAI 및 Gemini API 연동을 위해 다음 Key 정보들이 필요합니다. 실습 폴더(`.backend/GPT_document_self` 또는 `.backend/ocr_practice`)에 각각 `.env` 파일을 생성하고 작성합니다.

```env
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Gemini API 설정
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🚀 실습별 실행 방법

### 1. 기본 FastAPI 웹 서버 실행
FastAPI의 기본적인 동작을 실습합니다.
```bash
cd backend
uvicorn main:app --reload
```
* **확인**: 브라우저에서 `http://localhost:8000/` 또는 `http://localhost:8000/docs` 접속 (Swagger UI 제공)

---

### 2. 로컬 LLM (Ollama) 실습
로컬 PC에 Ollama가 설치되어 있어야 하며, Gemma3 모델 등이 다운로드되어 있어야 합니다 (`ollama run gemma3:1b`).

* **스트리밍 대답 확인 (CLI)**:
  ```bash
  cd backend/Ollama_practice
  python 01_stream.py
  ```
* **콘솔 기반 챗봇 실행**:
  ```bash
  python 02_chatBot.py
  ```
* **Ollama 연동 FastAPI 서버 실행**:
  ```bash
  uvicorn 03_useFastAPI:app --reload --port 8000
  ```

---

### 3. OpenAI GPT Structured Outputs 문서 요약 API
사용자가 전송한 텍스트를 OpenAI GPT를 활용해 정형화된 JSON 형태로 요약하여 반환하는 실습입니다.
```bash
cd backend/GPT_document_self
uvicorn app.main:app --reload --port 8000
```
* **Endpoint**: `POST /api/v1/summarize`
* **요청 예시**:
  ```json
  {
    "text": "요약하려는 긴 문서 본문 입력..."
  }
  ```
* **반환 구조 (Pydantic 강제 포맷)**:
  ```json
  {
    "data": {
      "summary": "문서의 세 줄 핵심 요약 내용",
      "keywords": ["키워드1", "키워드2"],
      "warnings": ["주의사항 및 누락 우려 정보"]
    },
    "model": "gpt-4o",
    "prompt_version": "v1.0",
    "response_id": "chatcmpl-..."
  }
  ```

---

### 4. OCR 3종 벤치마크 및 Gemini 요약 파이프라인
Tesseract, EasyOCR, PaddleOCR의 성능(글자 추출율, 속도)을 비교 분석하고, 가장 잘 정제된 본문을 Gemini Pro 모델을 사용해 교정 및 요약한 리포트(`ocr_result_report.txt`)를 작성합니다.

```bash
cd backend/ocr_practice
python main.py
```
* `sample.jpg` 또는 `sample.pdf`에 대한 다중 OCR 처리 수행
* 처리 성공 후, 생성된 `ocr_result_report.txt` 파일을 통해 엔진별 소요 시간 및 추출 글자수 비교 보고서를 확인합니다.

---

## 📝 참고 사항
* **Mock 모드**: OpenAI API 키가 아직 준비되지 않은 경우 `GPT_document_self`에서는 `mock_summarize_document`를 활성화하여 가짜 결과로 개발 흐름을 점검해볼 수 있습니다.
* **디버깅**: HTTP 호출 실패 시 FastAPI의 ExceptionHandler를 활용하여 `502 Bad Gateway` 및 `503 Service Unavailable` 등 상세 상태 코드를 사용자에게 표준화된 형태로 전달합니다.
