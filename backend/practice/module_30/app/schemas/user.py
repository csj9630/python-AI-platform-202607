from pydantic import BaseModel, ConfigDict


class UserCreateRequest(BaseModel):
    """사용자 생성 요청 DTO"""

    name: str
    email: str


class UserResponse(BaseModel):
    """사용자 응답 DTO"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str