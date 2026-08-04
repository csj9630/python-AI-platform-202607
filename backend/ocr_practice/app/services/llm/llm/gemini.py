# gemini.py
import os
from dotenv import load_dotenv
from baseLLM import BaseLLM

load_dotenv()

class GeminiLLM(BaseLLM):
    def __init__(self, model_name: str = "gemini-3.5-flash", temperature: float = 0.3):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = os.getenv("GEMINI_API_KEY")

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            return "[Gemini Error: .env 파일에 GEMINI_API_KEY가 존재하지 않습니다.]"
            
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=1000
                )
            )
            return response.text.strip()
        except Exception as e:
            return f"[Gemini Error: {e}]"