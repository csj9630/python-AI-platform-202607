import time
from app.services.ocr.base import BaseOCR

class TesseractOCR(BaseOCR):
    def __init__(self):
        self.name = "Tesseract OCR"

    def extract_text(self, image_path: str):
        start_time = time.time()
        try:
            import pytesseract
            from PIL import Image
            
            # Windows 환경에서 경로 문제 발생 시 주석 해제 후 수정
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang='kor+eng')
        except Exception as e:
            text = f"[Tesseract Error: {e}]"
        
        elapsed = time.time() - start_time
        return {
            "engine": self.name,
            "text": text.strip(),
            "elapsed_time": round(elapsed, 3)
        }