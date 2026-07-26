"""
Module 34: Exception Handling과 표준 오류 응답 - 사용자 정의 Business/Domain Exception 패턴

주요 핵심 학습 내용:
1. Layered Architecture에서는 Service/도메인 레이어가 FastAPI의 HTTPException에 직접 의존하기보다 사용자 정의 비즈니스 예외(Business Exception)를 발생시키는 것이 좋습니다.
2. 전역 Exception Handler(@app.exception_handler)는 도메인 예외를 감지하여 적절한 HTTP Status Code와 표준 JSON Response로 변환합니다.
3. Exception은 서버 내부의 실패 상황이고, Error Response는 이를 Client에게 전달하는 HTTP 응답입니다.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


# 사용자 정의 비즈니스/도메인 예외 클래스
# Service 레이어에서 FastAPI 의존성 없이 독립적으로 예외를 정의하여 사용합니다.
class DocmentNotFoundError(Exception):
    """문서를 찾지 못했을 때 발생시키는 비즈니스 예외"""
    pass


# 전역 Exception Handler 등록
# 지정한 도메인 예외(DocmentNotFoundError)가 발생했을 때 이를 가로채어
# HTTP Status Code(404) 및 일관된 표준 JSON 응답 구조(code, message)로 변환하여 반환합니다.
@app.exception_handler(DocmentNotFoundError)
async def handle_not_found(request: Request, error: DocmentNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "code": "DOCUMENT_NOT_FOUND",  # 클라이언트가 식별 가능한 오류 코드
            "message": str(error)         # 클라이언트에 전달할 오류 메시지
        }
    )


@app.get("/doucments/{document_id}")
def document(document_id: int):
    # 비즈니스 로직 수행 중 실패 시 return이 아닌 raise를 통해 예외를 발생시킵니다.
    raise DocmentNotFoundError(f"document {document_id}를 찾을 수 없습니다.")


'''
# backend 폴더 위치에서 실행

서버 시작:
> uvicorn module_34_self.domain_exception:app --reload

API 호출 (cURL 예시):
> curl "http://localhost:8000/documents/999"

예상 응답 (404 Not Found):
{
    "code": "DOCUMENT_NOT_FOUND",
    "message": "document 999를 찾을 수 없습니다."
}

'''