# 목표 : FastAPI를 활용하여 간단한 RESTful API 서버를 구축하고
# 브라우저에서 URL을 통해 API를 호출하여 응답을 확인하는 방법을 학습합니다.
from fastapi import FastAPI, status
from pydantic import BaseModel

# FastAPI 클래스에서 객체 생성
# 앞으로 API 관련 대부분은 app 객체를 통해서 처리
app = FastAPI() 

# 
class DocumentCreate(BaseModel):
    title: str

@app.post("/documents",status_code=status.HTTP_201_CREATED)
def create_document(request:DocumentCreate) -> dict[str,object]:
    return{"id":1, "title":request.title}

@app.get("/documents/{document_id}")
def get_document(document_id:int) -> dict[str,object]:
    return {"id":document_id, "title":"sample"}
