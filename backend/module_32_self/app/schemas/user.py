from pydantic import BaseModel

# DTO를 정의하는 클래스, BaseModel을 상속받아 자료형을 검증.
class UserResponse(BaseModel):
    id:int
    name:str
    email:str