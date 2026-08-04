from abc import ABC, abstractmethod
# 1. 공통 LLM 인터페이스
class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


