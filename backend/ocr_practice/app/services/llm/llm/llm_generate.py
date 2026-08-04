# 통합 실행 함수
# llm_generate.py
from typing import Optional
from baseLLM import BaseLLM
from gemma import OllamaGemmaLLM
from gemini import GeminiLLM
from prompts import PROMPT_MAP

def generate_llm_response(
    text: str,
    task_type: str = "proofread", # 'proofread', 'summary', 'translate' 또는 직접 작성한 prompt 템플릿
    provider: str = "gemma",      # 'gemma' (ollama) 또는 'gemini'
    model_name: Optional[str] = None,
    target_language: str = "영어" # task_type이 'translate'일 경우 사용
) -> str:
    """
    OCR 텍스트와 실행할 작업 종류, 사용 LLM을 받아 결과를 반환하는 메인 함수
    """
    # 1. 입력 텍스트 유효성 검사
    if not text or not text.strip():
        return "오류: 입력된 OCR 텍스트가 없습니다."

    # 2. LLM 구현체 객체 생성 (Provider 분기)
    provider_lower = provider.lower()
    
    if provider_lower in ["gemma", "ollama"]:
        target_model = model_name if model_name else "gemma3:1b"
        llm_client: BaseLLM = OllamaGemmaLLM(model_name=target_model)
        
    elif provider_lower == "gemini":
        target_model = model_name if model_name else "gemini-2.5-flash"
        llm_client: BaseLLM = GeminiLLM(model_name=target_model)
        
    else:
        return f"오류: 지원하지 않는 LLM 제공자입니다. ('{provider}')"

    # 3. 프롬프트 템플릿 가져오기 및 파라미터 바인딩
    if task_type in PROMPT_MAP:
        prompt_template = PROMPT_MAP[task_type]
    else:
        # 맵에 없는 직접 전달받은 커스텀 템플릿 문자열 처리
        prompt_template = task_type

    # 프롬프트 인자 치환 ({text}, {target_language} 등)
    formatted_prompt = prompt_template.format(
        text=text, 
        target_language=target_language
    )

    # 4. LLM 실행 후 결과 반환
    return llm_client.generate(formatted_prompt)


# --- 테스트 실행 예시 ---
#    result = generate_llm_response(sample_ocr, task_type="proofread", provider="gemma")
#    print(result)
