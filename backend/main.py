# 백엔드 진입점
# FastAPI는 Python 기반의 웹 프레임워크로, RESTful API를 빠르게 개발할 수 있도록 도와줍니다.
# 목표 : FastAPI를 활용하여 간단한 RESTful API 서버를 구축하고
# 브라우저에서 URL을 통해 API를 호출하여 응답을 확인하는 방법을 학습합니다.
from fastapi import FastAPI, status
from pydantic import BaseModel

# FastAPI 클래스에서 객체 생성
# 앞으로 API 관련 대부분은 app 객체를 통해서 처리
app = FastAPI() 

@app.get("/") # API 등록 :  "/" 경로에 GET 요청이 들어오면 home() 함수가 실행
def home():
    return {"message": "Hello FastAPI"} # fastapi는 dictinory를  기본적으로 JSON 형태로 응답을 반환

@app.get("/health") # API 등록 :  "/health" 경로에 GET 요청이 들어오면 home() 함수가 실행
def health_check():
    return{
        "status"   : "ok",
        "service" : "AI platform Engine",
        "message"  : "Health check successful",
    }


# * 실행
# uvicorn main:app --reload
# uvicorn [파일명]:[FastAPI 객체명] --reload
# => uvicorn으로 main.py 파일의 app 객체를 실행, 파일 수정 시 자동으로 서버 재시작

# * 확인 : localhost:8000/[url]