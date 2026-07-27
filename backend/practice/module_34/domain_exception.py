from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

'''
class DocumentNotFoundError(Exception):
    pass

@app.exception_handler(DocumentNotFoundError)
async def handle_not_found(request: Request, error: DocumentNotFoundError):
    return JSONResponse(status_code=404, content={"code": "DOCUMENT_NOT_FOUND", "message": str(error)})

@app.get("/documents/{document_id}")
def document(document_id: int):
    raise DocumentNotFoundError(f"document {document_id} not found")

'''

class DocumentNotFoundError(Exception):
    pass

@app.exception_handler(DocumentNotFoundError )
async def handle_not_found(request:Request, error: DocumentNotFoundError):
    return JSONResponse(status_code=404,content={"code" : "DOCUMENT_NOT_FOUND","message":str(error)})    

@app.get("/documents/{document_id}")
def document(document_id:int):
    raise DocumentNotFoundError(f"손님 문서{document_id}가 없습니다.")