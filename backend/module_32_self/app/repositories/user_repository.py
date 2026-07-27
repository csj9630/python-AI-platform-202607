"""
[의존성 주입 (Dependency Injection, DI) - 리포지토리 계층]
- 이 파일은 데이터 접근을 담당하는 Repository 클래스와 이를 주입할 Provider 함수를 정의합니다.
- DI 관점: UserService에 의존성(Dependency)으로 주입될 최하위 레이어 객체를 생성/제공합니다.
"""

from typing import Dict, Optional


# [의존성 대상 클래스]
# 데이터 저장소 역할을 수행하며, UserService에서 생성자 주입(Constructor Injection) 받아 사용합니다.
class UserRepository:
    def __init__(self):
        # 메모리 데이터베이스 역할의 더미 데이터 초기화
        self.users: Dict[int, dict] = {
            1: {
                "id": 1,
                "name": "라이언 레이놀즈",
                "email": "deadpool@xman.com",
            },
            2: {
                "id": 2,
                "name": "휴 잭맨",
                "email": "wooverlen@xman.com",
            },
        }

    # 사용자 ID 기반 데이터 조회 메서드
    def find_by_id(self, user_id: int) -> Optional[dict]:
        return self.users.get(user_id)


# [의존성 제공자 함수 (Dependency Provider)]
# FastAPI의 Depends()에서 호출되어 UserRepository 인스턴스를 생성 및 전달(주입)합니다.
def get_user_repository() -> UserRepository:
    return UserRepository()

