from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Options(BaseModel):
    top_k: int = 3
    language: str = "ko"

class SearchRequest(BaseModel):
    query: str
    options: Options

@app.post("/search")
def search(request: SearchRequest) -> dict[str, object]:
    return request.model_dump()
