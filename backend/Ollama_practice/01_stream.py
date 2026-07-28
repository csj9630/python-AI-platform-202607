from ollama import chat


stream = chat(
    model="gemma3:1b",
    messages=[
        {
            "role": "user",
            "content": "Python 함수가 무엇인지 쉽게 설명해 주세요.",
        }
    ],
    stream=True,
)

for chunk in stream:
    text = chunk.message.content
    print(text, end="", flush=True)

print()