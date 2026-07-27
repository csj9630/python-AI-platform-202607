from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 에러 응답 형식을 일관되게 고정하기 위한 DTO(Data Transfer Object) 역할을 합니다.
class ErrorResponse(BaseModel):
    code:str
    message:str

@app.get("/limited")
def limited() -> dict[str,str]: # 리턴값 dict[key str, value str]
    # 1. Pydantic 모델 인스턴스 생성 (에러 정보 채우기)
    detail = ErrorResponse(code="RATE_LIMITED", message="아아네문서?이걸말하는건가?")

    # 2. HTTPException 예외 발생
    # - status_code=404: 클라이언트에게 HTTP 404 (Not Found) 상태 코드를 반환
    # - detail=detail.model_dump(): Pydantic 모델 객체를 파이썬 dict(딕셔너리) 형태로 변환하여 detail에 전달
    #   (FastAPI가 이를 자동으로 JSON 응답 body로 변환해 줍니다)
    raise HTTPException(status_code=404,detail=detail.model_dump()) 
