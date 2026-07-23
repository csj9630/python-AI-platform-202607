from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.service.user_service import UserService, get_user_service

routers = APIRouter()

@routers.get(
    "/users/{user_id}",
    response_model=UserResponse,
)

def get_user(
    user_id : int,
    service:UserService = Depends(get_user_service),
):
    return service.get_user(user_id)