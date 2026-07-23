from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.service.user_service import UserService, get_user_service

routers = APIRouter()
'''
# 설명 : 특정 사용자 정보를 조회하는 엔드포인트
@routers.get(
    "/users/{user_id}", # 특정 사용자 정보를 조회하는 경로
    response_model=UserResponse, # 응답 모델을 UserResponse로 지정
)
def get_user( # 특정 사용자 정보를 조회하는 함수
    user_id: int, # 사용자 ID를 경로 매개변수로 받음
    service: UserService = Depends(get_user_service),# UserService 인스턴스를 의존성 주입으로 받음
):
    return service.get_user(user_id) # UserService의 get_user 메서드를 호출하여 사용자 정보를 반환
'''

@routers.get(
    "/users/{user_id}",
    response_model=UserResponse,
)

def get_user(
    
)
)