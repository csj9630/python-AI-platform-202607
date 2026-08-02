import os
from PIL import Image
import pytesseract

# Windows 환경에서 Tesseract 경로가 잡히지 않을 경우 주석 해제 후 수정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image_path: str) -> str:
    """
    이미지 파일 경로를 입력받아 OCR 텍스트를 추출하는 함수
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

    try:
        # 이미지 열기 및 OCR 실행 (한글+영어)
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image, lang='kor+eng')
        return extracted_text.strip()
    except Exception as e:
        raise RuntimeError(f"OCR 처리 중 오류 발생: {str(e)}")