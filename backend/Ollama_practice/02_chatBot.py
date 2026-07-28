from ollama import ResponseError, chat


MODEL_NAME = "gemma3:1b"

messages: list[dict[str, str]] = [ # typeHind
    {
        "role": "system",
        "content": (
            "당신은 Python 초보자를 돕는 강사입니다. "
            "전문 용어를 사용하면 바로 쉬운 말로 설명하세요."
        ),
    }
]


while True:
    question = input("\n사용자: ").strip()

    if question.lower() in {"exit", "quit", "종료"}:
        print("챗봇을 종료합니다.")
        break

    if not question:
        print("질문을 입력해 주세요.")
        continue

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    try:
        response = chat(
            model=MODEL_NAME,
            messages=messages,
        )
    except ResponseError as exc:
        print(f"Ollama 오류: {exc}")
        messages.pop()
        continue
    except OSError:
        print("Ollama Server 연결을 확인해 주세요.")
        messages.pop()
        continue

    answer = response.message.content.strip()

    if not answer:
        print("빈 응답을 받았습니다.")
        messages.pop()
        continue

    print(f"Assistant: {answer}")

    messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )