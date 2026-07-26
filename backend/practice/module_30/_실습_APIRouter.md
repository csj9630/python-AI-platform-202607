## Module 30. APIRouter와 기능별 모듈 분리

### 핵심 내용 정리

이번 Unit에서는 **APIRouter와 기능별 모듈 분리**를 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **APIRouter는 기능별 Endpoint를 관리하는 독립적인 Router 객체**이다.
- `main.py`는 API를 작성하는 곳이 아니라 **각 Router를 조립(Composition)하는 곳**이다.
- Router는 기능(Chat, OCR, Document 등) 단위로 분리하는 것이 실무 표준이다.
- `prefix`와 `tags`를 활용하면 URL 관리와 Swagger 문서 구성이 훨씬 쉬워진다.
- Router는 Endpoint만 담당하고, Business Logic은 Service Layer에 두는 것이 AI Backend의 기본 설계 원칙이다.
