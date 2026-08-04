import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def hybrid_pdf_ocr(pdf_path: str, text_threshold: int = 50) -> dict:
    """
    하이브리드 방식으로 PDF에서 텍스트를 추출합니다.
    - 텍스트 레이어가 있는 페이지: 직접 추출 (빠르고 100% 정확)
    - 텍스트 레이어가 없는 페이지: 이미지로 렌더링 후 OCR 처리
    """
    results = {}
    
    try:
        # PDF 문서 열기
        with fitz.open(pdf_path) as pdf_doc:
            # Windows 환경에서 경로 문제 발생 시 주석 해제 후 수정
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                
                # 1단계: 디지털 텍스트 직접 추출 시도
                extracted_text = page.get_text("text").strip()
                
                # 2단계: 추출된 텍스트 길이를 기준으로 OCR 필요 여부 판별
                # 의미 있는 텍스트(예: 50자 이상)가 추출되었다면 디지털 페이지로 간주
                if len(extracted_text) > text_threshold:
                    results[page_num + 1] = {
                        "method": "direct_extraction",
                        "text": extracted_text
                    }
                else:
                    # 텍스트가 부족하거나 없는 경우 (스캔본/이미지 페이지로 간주)
                    # 3단계: 페이지를 고해상도 이미지(Pixmap)로 렌더링
                    zoom_matrix = fitz.Matrix(2, 2)  # 해상도 향상 (DPI 약 144)
                    pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)
                    
                    # Pixmap을 PIL Image로 변환
                    img_bytes = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_bytes))
                    
                    # 4단계: 이미지에 OCR 적용
                    ocr_text = pytesseract.image_to_string(img, lang='kor+eng').strip()
                    
                    results[page_num + 1] = {
                        "method": "ocr_inference",
                        "text": ocr_text
                    }
                    
    except Exception as e:
        print(f"PDF 처리 중 오류 발생: {e}")
        
    return results

# 사용 예시
if __name__ == "__main__":
    sample_pdf = "hybrid_sample.pdf"
    extracted_data = hybrid_pdf_ocr(sample_pdf)
    
    for page_num, data in extracted_data.items():
        print(f"--- 페이지 {page_num} [{data['method']}] ---")
        print(data['text'][:10000] + "...\n")
