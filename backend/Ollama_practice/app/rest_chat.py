import requests


def main() -> None:
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "gemma3:1b",
            "messages": [
                {
                    "role": "user",
                    "content": "Local LLM의 장점을 세 가지 설명해 주세요.",
                }
            ],
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()
    print(data["message"]["content"])


if __name__ == "__main__":
    main()
