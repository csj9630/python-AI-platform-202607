from typing import Dict, Optional

class UserRepository:
    def __init__(self):
        self.users: Dict[int, dict] = {
            1: {
                "id": 1,
                "name": "김상수",
                "email": "sangsoo@example.com",
            },
            2: {
                "id": 2,
                "name": "홍길동",
                "email": "gildong@example.com",
            },
        }

    def find_by_id(self, user_id: int) -> Optional[dict]:
        return self.users.get(user_id)

def get_user_repository() -> UserRepository:
    return UserRepository()