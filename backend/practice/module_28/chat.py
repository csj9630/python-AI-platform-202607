from fastapi import FastAPI
#from module29.chat_service import ChatService
from chat_service import ChatService
app = FastAPI()

@app.post("/chat")
def chat():

    service = ChatService()

    return service.chat()