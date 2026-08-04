import ollama
from baseLLM import BaseLLM

class OllamaGemmaLLM(BaseLLM):
    def __init__(self, model_name: str = "gemma3:1b", temperature: float = 0.3):
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": self.temperature,
                    "num_predict": 1000
                }
            )
            return response['response'].strip()
        except Exception as e:
            return f"[Ollama Gemma Error: {e}]\n(Ollama 데몬 실행 여부를 확인해 주세요.)"