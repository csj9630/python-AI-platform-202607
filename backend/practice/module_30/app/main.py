from fastapi import FastAPI

from .routers import users


app = FastAPI(
    title="APIRouter 예제",
)


app.include_router(users.router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "FastAPI 서버가 실행 중입니다.",
    }