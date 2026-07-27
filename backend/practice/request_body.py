from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


""" 
# 수집할 json 데이터 구조 정의
item class를 baseModel을 상속받아 정의합니다.
"""
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

# API 엔드포인트에서 데이터 읽기
@app.post("/items")
async def create_item(item: Item):
    # FastAPI는 pydantic 모델을 호출하여, 요청 본문에서 JSON 데이터를 읽고, 이를 Item 모델로 변환합니다.
    return {"message": "Item created successfully", "item_data": item}
