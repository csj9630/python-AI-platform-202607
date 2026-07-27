# Module 34. Exception Handling과 표준 오류 응답

이번 Unit에서는 **Exception Handling과 표준 오류 응답 설계**를 학습했습니다. 반드시 기억해야 할 내용은 다음과 같습니다.

- Exception은 서버 내부의 실패 상황이고, Error Response는 이를 Client에게 전달하는 HTTP 응답이다.
- `HTTPException`은 단순한 HTTP 오류를 표현할 때 사용할 수 있으며 `return`이 아니라 `raise`한다.
- Layered Architecture에서는 Service가 FastAPI의 `HTTPException`에 직접 의존하기보다 사용자 정의 Business Exception을 발생시키는 것이 좋다.
- 전역 Exception Handler는 Exception을 Status Code와 표준 JSON Response로 변환한다.
- Validation 오류, Business 오류, 외부 시스템 오류, 예상하지 못한 서버 오류를 구분해야 한다.
- Error Response는 `code`, `message`, `status`, `request_id`, `details`처럼 일관된 구조를 사용하는 것이 좋다.
- 예상하지 못한 오류의 상세 정보는 Server Log에 기록하고 Client에게는 안전한 메시지만 반환한다.
- Middleware에서 Request ID를 추가한 경우 오류 응답과 로그에 연결하면 운영 중 문제를 추적하기 쉬워진다.
