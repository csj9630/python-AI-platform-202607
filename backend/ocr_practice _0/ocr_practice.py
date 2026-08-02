import os
from PIL import Image
import pytesseract

# -------------------------------------------------------------------
# [Windows 사용자 전용 설정]
# Tesseract가 환경변수(PATH)에 등록되지 않은 경우 아래 주석을 해제하고 설치 경로를 지정하세요.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# -------------------------------------------------------------------

def run_ocr_test(image_path: str):
    # 1. 이미지 파일 존재 여부 확인
    if not os.path.exists(image_path):
        print(f"❌ 에러: [{image_path}] 파일을 찾을 수 없습니다.")
        return

    try:
        print(f"📷 이미지 읽는 중: {image_path}")
        # 2. PIL 라이브러리로 이미지 열기
        image = Image.open(image_path)

        print("🔍 OCR 텍스트 추출 진행 중...")
        # 3. OCR 수행 (lang='kor+eng' : 한글 + 영어 동시 인식)
        extracted_text = pytesseract.image_to_string(image, lang='kor+eng')

        print("\n================ [ 추출 결과 ] ================")
        if extracted_text.strip():
            print(extracted_text.strip())
        else:
            print("(텍스트를 인식하지 못했거나 빈 이미지입니다.)")
        print("===============================================")

    except Exception as e:
        print(f"❌ OCR 실행 중 오류 발생: {e}")
        print("💡 TIP: Tesseract-OCR이 PC에 올바르게 설치되었는지 확인하세요.")

if __name__ == "__main__":
    # 테스트할 이미지 파일 경로 지정 (같은 폴더에 sample.png 준비)
    TEST_IMAGE_PATH = "sample.jpg" 
    
    run_ocr_test(TEST_IMAGE_PATH)