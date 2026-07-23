from fastapi import FastAPI

from app.routers import users


app = FastAPI(
    title="Dependency Injection 예제",
)

# include routers란? 
# - routers를 include하면, 해당 routers에 정의된 경로들이 API 문서에 자동으로 추가됨
app.include_router(users.routers)
