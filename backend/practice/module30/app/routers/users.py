from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserCreateRequest, UserResponse


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# DB 대신 사용하는 임시 메모리 저장소
users: list[dict] = [
    {
        "id": 1,
        "name": "Kim",
        "email": "kim@example.com",
    }
]


@router.get(
    "",
    response_model=list[UserResponse],
)
def get_users() -> list[dict]:
    """전체 사용자 조회"""

    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(user_id: int) -> dict:
    """사용자 한 명 조회"""

    for user in users:
        if user["id"] == user_id:
            return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="사용자를 찾을 수 없습니다.",
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(request: UserCreateRequest) -> dict:
    """사용자 생성"""

    new_user = {
        "id": len(users) + 1,
        "name": request.name,
        "email": request.email,
    }

    users.append(new_user)

    return new_user