import os
import time
from app.services.ocr.base import BaseOCR

# PIR 연산 오작동 방지
os.environ["FLAGS_enable_pir_api"] = "0"

class PaddleOCRService(BaseOCR):
    def __init__(self):
        self.name = "PaddleOCR"
        self.ocr = None

    def _get_ocr_instance(self):
        if self.ocr is None:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(
                use_angle_cls=True, 
                lang='korean', 
                enable_mkldnn=False
            )
        return self.ocr

    def extract_text(self, image_path: str):
        start_time = time.time()
        
        try:
            from paddleocr import PaddleOCR
        except ImportError:
            return {
                "engine": self.name,
                "text": "[PaddleOCR 패키지 미설치로 스킵됨]",
                "elapsed_time": round(time.time() - start_time, 3)
            }

        try:
            ocr = self._get_ocr_instance()
            results = ocr.ocr(image_path)
            
            text_lines = []
            
            if results:
                for res in results:
                    if not res:
                        continue
                    
                    # 1. 최신 PaddleX / PaddleOCR Dict 반환 구조 대응
                    if isinstance(res, dict):
                        # rec_texts 키에 실제 추출된 텍스트 리스트가 담겨 있음
                        if 'rec_texts' in res:
                            text_lines.extend([str(t) for t in res['rec_texts']])
                        elif 'text' in res:
                            text_lines.append(str(res['text']))
                    
                    # 2. 기존 표준 List 반환 구조 대응: [[[box], (text, score)], ...]
                    elif isinstance(res, list):
                        for line in res:
                            if isinstance(line, dict):
                                if 'rec_texts' in line:
                                    text_lines.extend([str(t) for t in line['rec_texts']])
                                elif 'text' in line:
                                    text_lines.append(str(line['text']))
                            elif isinstance(line, (list, tuple)) and len(line) >= 2:
                                if isinstance(line[1], (list, tuple)) and len(line[1]) > 0:
                                    text_lines.append(str(line[1][0]))

            text = "\n".join(text_lines)
            if not text.strip():
                text = "(PaddleOCR 추출 결과가 없습니다.)"

        except Exception as e:
            print(f"❌ [PaddleOCR 실행 에러]: {e}")
            text = f"[PaddleOCR 실행 실패: {e}]"

        elapsed = time.time() - start_time
        return {
            "engine": self.name,
            "text": text.strip(),
            "elapsed_time": round(elapsed, 3)
        }