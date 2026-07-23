from typing import Dict, Optional

# 설명
class UserRepository:
    def __init__(self):
        self.users:Dict[int,dict]={
            1:{
                "id":1,
                "name":"라이언 레이놀즈",
                "email":"deadpool@xman.com",
            },
            2:{
                "id":2,
                "name":"휴 잭맨",
                "email":"wooverlen@xman.com",
            },
        }
    def find_by_id(self,user_id:int)->Optional[dict]:
        return self.users.get(user_id)


def get_user_repository() -> UserRepository:
    return UserRepository()

