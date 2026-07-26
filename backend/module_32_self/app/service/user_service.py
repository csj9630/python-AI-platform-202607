"""
[의존성 주입 (Dependency Injection, DI) - 서비스 계층]
- 비즈니스 로직을 처리하는 클래스입니다.
- UserRepository를 직접 내부에서 생성하지 않고 외부에서 전달받는 '생성자 주입(Constructor Injection)' 방식을 사용합니다.
- 이를 통해 서비스 레이어와 저장소 레이어 간의 결합도를 낮추고(Loose Coupling), 테스트 시 Mock Repository로 쉽게 대체할 수 있습니다.
"""

from fastapi import Depends
from fastapi.exceptions import HTTPException
from app.repositories.user_repository import UserRepository, get_user_repository


# [의존성을 주입받는 비즈니스 로직 클래스]
class UserService:
    # 1. 생성자 주입 (Constructor Injection)
    # UserService 생성 시 외부에서 의존성(UserRepository)을 주입받아 인스턴스 변수에 저장합니다.
    def __init__(self, repository: UserRepository):
        self.repository = repository  # 주입받은 의존성 객체 활용

    def get_user(self, user_id: int) -> dict:
        # 주입받은 repository를 활용하여 데이터 조회
        user = self.repository.find_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="우린 그가 누군지 모른다.",
            )

        return user


# [의존성 제공자 함수 (Dependency Provider) 및 의존성 체인(Nested DI)]
# FastAPI의 Depends(get_user_repository)를 통해 먼저 UserRepository 객체를 주입받고,
# 이를 UserService 생성자에 전달하여 UserService 인스턴스를 최종 반환하는 DI Chain 역할을 수행합니다.
def get_user_service(
    repository: UserRepository = Depends(get_user_repository),  # UserRepository 의존성 주입
) -> UserService:
    return UserService(repository)  # 주입받은 의존성을 가지고 UserService 인스턴스 생성 후 주입
