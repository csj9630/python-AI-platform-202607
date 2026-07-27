# 역할: OpenAI SDK 호출, Structured Outputs 파싱, Custom Exception 정의

import os
from openai import OpenAI
from dotenv import load_dotenv

from app.prompts import PROMPT_VERSION, SUMMARY_INSTRUCTIONS, build_summary_input
from app.schemas import SummaryResult, SummaryServiceResult

load_dotenv()


class SummaryConfigurationError(RuntimeError):
    """서버 환경 변수나 API Key 미설정 시 발생"""
    pass


class SummaryUpstreamError(RuntimeError):
    """OpenAI API 응답 실패 또는 파싱 불가 시 발생"""
    pass


def summarize_document(text: str) -> SummaryServiceResult:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    if not api_key:
        raise SummaryConfigurationError("OPENAI_API_KEY가 설정되지 않았습니다.")

    client = OpenAI(api_key=api_key)

    try:
        # Structured Outputs: Pydantic Schema를 인자로 전달
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": SUMMARY_INSTRUCTIONS},
                {"role": "user", "content": build_summary_input(text)},
            ],
            response_format=SummaryResult,
        )
    except Exception as exc:
        raise SummaryUpstreamError(f"OpenAI API 호출 실패: {str(exc)}") from exc


    parsed = response.choices[0].message.parsed
    if parsed is None:
        raise SummaryUpstreamError("구조화된 요약 결과를 생성하지 못했습니다.")

    return SummaryServiceResult(
        data=parsed,
        model=model,
        prompt_version=PROMPT_VERSION,
        response_id=getattr(response, "id", None),
    )


def mock_summarize_document(text: str) -> SummaryServiceResult:
    """테스트용 Mock 가짜 데이터 반환 함수"""
    mock_data = SummaryResult(
        summary="이 문서는 테스트용으로 생성된 가짜 요약 결과입니다.",
        keywords=["테스트", "FastAPI", "Mock"],
        warnings=["실제 API 키가 적용되지 않은 상태입니다."]
    )

    return SummaryServiceResult(
        data=mock_data,
        model="mock-gpt-4o",
        prompt_version="v1.0-mock",
        response_id="mock-resp-1234"
    )