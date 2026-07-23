# 백엔드 진입점
from fastapi import FastAPI
# from module_32_self.app.routers import users
from app.routers import users

# FastAPI 클래스에서 객체 생성
# 앞으로 API 관련 대부분은 app 객체를 통해서 처리
app = FastAPI(
    title="Dependency Injection을 실습합니다."
) 

app.include_router(users.routers)


'''
# * 실행
uvicorn module_32_self.main:app --reload
=> uvicorn으로 module_32_self 폴더 > main.py > app 객체를 실행, 파일 수정 시 자동으로 서버 재시작
* 확인 : localhost:8000/[url]
'''