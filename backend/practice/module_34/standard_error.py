from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ErrorResponse(BaseModel):
    code: str
    message: str

@app.get("/limited")
def limited() -> dict[str, str]:
    detail = ErrorResponse(code="RATE_LIMITED", message="잠시 후 다시 시도하세요.")
    raise HTTPException(status_code=429, detail=detail.model_dump())
