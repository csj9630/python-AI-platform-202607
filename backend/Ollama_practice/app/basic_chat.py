from ollama import chat


def main() -> None:
    response = chat(
        model="gemma3:1b",
        messages=[
            {
                "role": "user",
                "content": "Ollama를 한 문장으로 설명해 주세요.",
            }
        ],
    )

    print(response.message.content)


if __name__ == "__main__":
    main()

    