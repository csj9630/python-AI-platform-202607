import os
from ollama import ResponseError, chat


MODEL_NAME = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:1b",
)

SYSTEM_PROMPT = """
당신은 문서 분석 도우미입니다.

규칙:
1. 사용자가 제공한 문서와 대화 내용 안에서만 답하세요.
2. 문서에 근거가 없으면 모른다고 답하세요.
3. 초보자가 이해할 수 있는 쉬운 문장으로 설명하세요.
""".strip()


def create_initial_messages(
    document: str,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                "다음 문서를 기억하고 이후 질문에 답하세요.\n\n"
                f"<document>\n{document}\n</document>"
            ),
        },
    ]


def ask(
    messages: list[dict[str, str]],
    question: str,
) -> str:
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("질문은 비어 있을 수 없습니다.")

    messages.append(
        {
            "role": "user",
            "content": cleaned_question,
        }
    )

    try:
        response = chat(
            model=MODEL_NAME,
            messages=messages,
        )
    except ResponseError as exc:
        messages.pop()
        raise RuntimeError(
            f"Ollama가 요청을 처리하지 못했습니다: {exc}"
        ) from exc
    except OSError as exc:
        messages.pop()
        raise RuntimeError(
            "Ollama Server 연결을 확인해 주세요."
        ) from exc

    answer = response.message.content.strip()

    if not answer:
        messages.pop()
        raise RuntimeError("모델의 응답이 비어 있습니다.")

    messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    return answer


def main() -> None:
    document = """
2026년 2학기 수강 변경 기간은 8월 24일부터 8월 28일까지다.
변경 신청은 학사 시스템에서 진행한다.
마감 이후에는 담당 부서의 별도 승인이 필요하다.
""".strip()

    messages = create_initial_messages(document)

    print(f"사용 모델: {MODEL_NAME}")
    print("종료하려면 exit를 입력하세요.")

    while True:
        question = input("\n사용자: ").strip()

        if question.lower() in {"exit", "quit", "종료"}:
            print("프로그램을 종료합니다.")
            break

        try:
            answer = ask(messages, question)
        except ValueError as exc:
            print(f"입력 오류: {exc}")
            continue
        except RuntimeError as exc:
            print(f"실행 오류: {exc}")
            continue

        print(f"Assistant: {answer}")


if __name__ == "__main__":
    main()