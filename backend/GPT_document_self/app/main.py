# 역할: FastAPI 라우터 및 HTTP Status Code 매핑

from fastapi import FastAPI, HTTPException, status
from app.schemas import SummaryRequest, SummaryServiceResult
from app.services.gpt_summary import (
    SummaryConfigurationError,
    SummaryUpstreamError,
    # summarize_document,
    mock_summarize_document,
)

app = FastAPI(title="Document AI Summary Service")

@app.post(
    "/api/v1/summarize",
    response_model=SummaryServiceResult,
    status_code=status.HTTP_200_OK,
)


# **************************************************************************
# 현재 이 함수는 더미 데이터만 반환 중입니다.
# 실제로는 summarize_document를 호출해서 사용해야 합니다.. 
# **************************************************************************

def create_summary(request: SummaryRequest) -> SummaryServiceResult:
    try: 
        # *******테스트 시 mock_summarize_document 호출 (실제 운영 시 summarize_document로 변경 가능)
        return mock_summarize_document(request.text)
        # return summarize_document(request.text)

    except SummaryConfigurationError as exc:
        # 서버 설정 문제 -> 503
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 요약 서비스 설정에 문제가 있습니다.",
        ) from exc

    except SummaryUpstreamError as exc:
        # 상위 API 연동/파싱 문제 -> 502
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI 모델 응답을 처리하지 못했습니다.",
        ) from exc

'''
# backend/GPT_document_self 폴더에서 실행
uvicorn app.main:app --reload
'''