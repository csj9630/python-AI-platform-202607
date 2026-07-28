from ollama import chat


def main() -> None:
    chunks = chat(
        model="gemma3:1b",
        messages=[
            {
                "role": "user",
                "content": "Ollama Server의 역할을 쉽게 설명해 주세요.",
            }
        ],
        stream=True,
    )

    for chunk in chunks:
        print(
            chunk.message.content,
            end="",
            flush=True,
        )

    print()


if __name__ == "__main__":
    main()