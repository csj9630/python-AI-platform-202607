from fastapi import Depends
from fastapi.exceptions import HTTPException
from app.repositories.user_repository import UserRepository, get_user_repository

class UserService:
    def __init__(self,repository : UserRepository):
        self.repository = repository

    def get_user(self, user_id:int) -> dict:
        user = self.repository.find_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="우린 그가 누군지 모른다.",
            )

        return user

def get_user_service(
        repository:UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)