"""
[의존성 주입 (Dependency Injection, DI) - 라우터/표현 계층]
- 표현 계층(Presentation Layer / Controller)으로 HTTP 요청을 수신하고 응답을 반환합니다.
- FastAPI의 `Depends()` 프레임워크 기능을 활용하여 핸들러 메서드에 UserService 객체를 주입(Method Parameter Injection)받습니다.
"""

# FastAPI 모듈에서 라우터 생성(APIRouter) 및 의존성 주입(Depends) 기능을 임포트합니다.
from fastapi import APIRouter, Depends
# 사용자 응답 데이터의 스키마(DTO) 클래스를 임포트합니다.
from app.schemas.user import UserResponse
# UserService 및 의존성 주입 Provider 함수(get_user_service)를 임포트합니다.
from app.service.user_service import UserService, get_user_service

# 사용자 관련 API 경로(엔드포인트)들을 그룹화할 APIRouter 인스턴스를 생성합니다.
routers = APIRouter()


# "/users/{user_id}" 경로로 들어오는 GET 요청을 처리하고, 응답 데이터 형식을 UserResponse로 지정합니다.
@routers.get(
    "/users/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,  # URL 경로 파라미터로 전달받는 사용자 ID (정수형)
    # [FastAPI 의존성 주입 (Parameter Injection)]
    # Depends(get_user_service)를 지정하면 요청 수신 시 FastAPI DI 컨테이너가:
    # 1) get_user_repository()를 실행하여 UserRepository 생성
    # 2) get_user_service()를 실행하여 UserService에 Repository 주입 및 인스턴스 생성
    # 3) 전달된 UserService 객체를 최종적으로 service 매개변수에 주입(Inject)해 줍니다.
    service: UserService = Depends(get_user_service),
):
    # 라우터는 UserService의 내부 구현이나 Repository 데이터 저장 방식에 대해 알 필요 없이,
    # 주입받은 service 객체의 get_user() 메서드를 호출하여 결과를 반환합니다.
    return service.get_user(user_id)
