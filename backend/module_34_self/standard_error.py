"""
Module 34: Exception Handling과 표준 오류 응답 - HTTPException 및 표준 오류 구조

주요 핵심 학습 내용:
1. HTTPException은 단순한 HTTP 오류 상황을 표현할 때 사용하며, `return`이 아니라 `raise`하여 예외를 발생시킵니다.
2. Error Response는 `code`, `message`와 같은 일관된 구조(Pydantic BaseModel 등)를 사용하여 클라이언트에게 전달합니다.
"""

from email import message
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# 일관된 Error Response 구조를 정의하는 Pydantic 모델
# (실무에서는 code, message, status, request_id, details 등의 구조를 활용)
class ErrorResponse(BaseModel):
    code: str
    message: str


@app.get("/limited")
def limited() -> dict[str, str]:
    # 표준화된 오류 응답 객체 생성
    detail = ErrorResponse(code="RATE_LIMITED", message="잠시후 다시 시도하세요")
    
    # HTTPException은 return이 아닌 raise를 사용하여 전달합니다.
    # status_code: HTTP 상태 코드 (429 Too Many Requests)
    # detail: 클라이언트에 전달할 표준 에러 JSON 구조 (Pydantic 모델을 dict로 변환)
    raise HTTPException(status_code=429, detail=detail.model_dump())



'''
# backend 폴더 위치에서 실행

서버 시작:
> uvicorn module_34_self.standard_error:app --reload

API 호출 (cURL 예시):
> curl "http://localhost:8000/documents/999"

예상 응답 (404 Not Found):
{
    "code": "DOCUMENT_NOT_FOUND",
    "message": "document 999를 찾을 수 없습니다."
}

'''