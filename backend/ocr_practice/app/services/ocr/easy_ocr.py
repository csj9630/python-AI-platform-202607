import time
from app.services.ocr.base import BaseOCR

class EasyOCRService(BaseOCR):
    def __init__(self):
        self.name = "EasyOCR"
        self.reader = None

    def extract_text(self, image_path: str):
        start_time = time.time()
        try:
            import easyocr
            if self.reader is None:
                # CPU 모드로 실행
                self.reader = easyocr.Reader(['ko', 'en'], gpu=False)
            
            results = self.reader.readtext(image_path, detail=0)
            text = "\n".join(results)
        except Exception as e:
            text = f"[EasyOCR 실행 오류: {e}]"
        
        elapsed = time.time() - start_time
        return {
            "engine": self.name,
            "text": text.strip(),
            "elapsed_time": round(elapsed, 3)
        }