import ollama

class OllamaLLM:
    def __init__(self, model_name: str = "gemma3:1b"):
        self.model_name = model_name

    def summarize(self, text: str) -> str:
        if not text.strip():
            return "요약할 텍스트가 존재하지 않습니다."
            
        prompt = f"""
다음은 문서에서 추출된 OCR 텍스트입니다. 
추출 텍스트를 json 형태로 정리해주세요.
[OCR 텍스트]
{text}
"""
#         prompt = f"""
# 다음은 문서에서 추출된 OCR 텍스트입니다. 
# 문맥을 파악하고 오타를 보정하여 3줄로 핵심 요약을 작성해 주세요.
# 출력형식 : 
# 1.
# 2.
# 3.
# [OCR 텍스트]
# {text}
# """
        try:
            # Ollama 로컬 모델 호출
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.3,
                    "num_predict": 1000  # max_output_tokens 역할
                }
            )
            return "gemma 요약 내용 : \n"+response['response'].strip()
            
        except Exception as e:
            return f"[Ollama 요약 실패: {e}]\n(Ollama 앱이 실행 중인지 확인해 주세요.)"
