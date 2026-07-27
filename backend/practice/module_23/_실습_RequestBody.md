### 핵심 내용 정리

이번 Unit에서는 **Request Body를 단순한 문법이 아니라 HTTP와 객체(Object) 전달 관점**에서 학습했습니다.

반드시 기억해야 할 내용은 다음과 같습니다.

- **Request Body는 서버에 전달할 실제 데이터를 담는 공간**이다.
- GET은 주로 **Path와 Query**를 사용하고, POST는 **Body**를 사용한다.
- 현대 REST API에서는 **JSON이 표준 데이터 형식**이다.
- React는 JavaScript 객체를 JSON으로 변환하여 Body에 담아 전송한다.
- FastAPI는 이 JSON을 다음 단계에서 **Pydantic을 이용해 Python 객체로 변환**한다.

---
