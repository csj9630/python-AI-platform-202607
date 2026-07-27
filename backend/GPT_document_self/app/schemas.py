# 역할: API 입출력 및 GPT Structured Outputs에 사용할 Pydantic Schema 정의
from pydantic import warnings
from pydantic import BaseModel, Field

# 1. API 클라이언트 요청 Schema
class SummaryRequest(BaseModel):
    text:str = Field(
        ..., # 의미 : 필수값, 파이썬의 None이 아님
        min_length=20,
        description="요약할 원문 텍스트 (최소 20자 이상)",
    )

# 2. GPT Structured Outputs 추출용 Schema
class SummaryResult(BaseModel):
    summary: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="문서의 핵심 요약 내용",
    )
    keywords:list[str]=Field(
        ...,
        max_length=5,
        description="주요 키워드 목록 (최대 5개)"
    )
    warnings:list[str]=Field(
        default_factory=list,
        description="문서 내 주요 주의사항이나 위험 요소"
    )

# 3. 최종 API 응답 Wrapper Schema
class SummaryServiceResult(BaseModel):
    data: SummaryResult
    model: str
    prompt_version: str
    response_id: str | None = None