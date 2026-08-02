import os
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

    def summarize(self, text: str) -> str:
        if not text.strip():
            return "요약할 텍스트가 존재하지 않습니다."
        if not self.api_key:
            return "[Gemini Error: .env 파일에 GEMINI_API_KEY가 없습니다.]"
            
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=self.api_key)
            prompt = f"""
다음은 문서에서 추출된 OCR 텍스트입니다. 
문맥을 파악하고 오타를 보정하여 3줄로 핵심 요약을 작성해 주세요.

[OCR 텍스트]
{text}
"""
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            return response.text.strip()
        except Exception as e:
            return f"[Gemini 요약 실패: {e}]"