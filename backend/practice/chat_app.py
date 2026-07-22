from fastAPI import FastAPI # FastAPI 클래스 임포트
app = FastAPI() # FastAPI 클래스에서 객체 생성

# GET 요청으로 Query Parameter(?question=...)를 전달받는 엔드포인트
@app.get("/ask") # /ask 경로에 GET 요청이 들어오면 ask_question() 함수가 실행
def ask_question(question: str = "질문이 비었습니다."):
    """
    URL 파라미터(question)를 입력받아 AI 응답 형태의 JSON으로 반환하는 함수
    - question: str (타입 힌트 적용)
    - 기본값: 파라미터 미입력 시 "질문이 비었습니다." 사용
    """
    return { # 요청에 대해 JSON 형태로 응답을 반환
        "user_question": question,
        "ai_answer": f"입력하신 질문은 '[{question}]'입니다." 
    }
