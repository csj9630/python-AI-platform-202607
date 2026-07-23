from fastapi import Depends
from fastapi.exceptions import HTTPException
from app.repositories.user_repository import UserRepository, get_user_repository

class UserService:
    # 생성자 : repository를 주입받아 UserService 인스턴스 생성
    def __init__(self, repository: UserRepository):
        self.repository = repository

    # 사용자 ID로 사용자 정보를 조회하는 메서드
    def get_user(self, user_id: int) -> dict:
        user = self.repository.find_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="사용자를 찾을 수 없습니다.",
            )

        return user

# FastAPI의 Depends를 사용하여 UserService 인스턴스를 생성하는 함수
def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)