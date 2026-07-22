# 폴더 구조
module30/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── users.py
│   │
│   └── schemas/
│       ├── __init__.py
│       └── user.py
│
└── requirements.txt

# 각 폴더별 역할

main.py
→ FastAPI 앱 생성
→ 각각의 router 등록

routers/users.py
→ 사용자 관련 URL과 함수 정의

schemas/user.py
→ 사용자 요청·응답 데이터 구조 정의

# 개발환경 라이브러리 설치 명령
pip install -r requirements.txt