import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# .env 파일의 환경 변수 로드
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def summarize_text(text: str) -> str:
    """
    텍스트를 입력받아 Gemini 2.5 Flash 모델로 핵심 요약을 수행하는 함수
    """
    if not text.strip():
        return "요약할 텍스트가 존재하지 않습니다."

    if not GEMINI_API_KEY:
        raise ValueError(".env 파일에서 GEMINI_API_KEY를 찾을 수 없습니다.")

    # Gemini Client 생성
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
다음은 문서에서 추출한 OCR 텍스트입니다. 
문맥을 파악하고 오타가 있다면 보정하여 아래 양식으로 요약해 주세요.

[요약 양식]
1. (문서 개요): 
2. (핵심 내용): 
3. (결론 및 조치사항): 

[OCR 텍스트]
{text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=700
            )
        )
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API 호출 오류: {str(e)}")