document-ai-lab/
├── .env                  # OpenAI API Key 및 환경변수
├── .gitignore            # Git 제외 설정 (.env, .vscode 등)
├── requirements.txt      # 의존성 패키지 목록
└── app/
    ├── __init__.py
    ├── main.py           # FastAPI 엔드포인트 및 HTTP 예외 처리
    ├── schemas.py        # Pydantic 기반 요청/응답 Schema 정의
    ├── prompts.py        # Prompt 지시문(Instructions) 관리
    └── services/
        ├── __init__.py
        └── gpt_summary.py# OpenAI SDK 호출 및 Business Logic