from typing import Protocol

class AIClient(Protocol):
    def generate(self, prompt: str) -> str: ...

class FakeClient:
    def generate(self, prompt: str) -> str:
        return f"fake: {prompt}"

class ChatService:
    def __init__(self, client: AIClient):
        self.client = client

    def chat(self, question: str) -> str:
        return self.client.generate(question)

print(ChatService(FakeClient()).chat("Composition?"))
