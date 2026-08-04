import re, os
from pathlib import Path
import pymupdf4llm
import pytesseract
from PIL import Image

def process_hybrid_ocr_with_image_text_inline(pdf_path: str, output_md_path: str):
    image_dir = "extracted_img"
    
    # 1. pymupdf4llm 실행 (비텍스트/이미지 영역을 이미지 파일로 크롭 저장)
    md_text = pymupdf4llm.to_markdown(
        doc=pdf_path,
        write_images=True,
        image_path=image_dir,
        image_format="png",
        dpi=300
    )

    # 2. 이미지 태그 정규식 패턴 탐색: ![](extracted_img/파일명.png)
    image_tag_pattern = re.compile(r'!\[\]\((extracted_img/[^\)]+)\)')
    matches = image_tag_pattern.findall(md_text)

    # 3. 각 이미지 파일에 대해 OCR을 수행하고, 태그 위치를 추출된 텍스트로 치환
    for img_path_str in matches:
        img_path = Path(img_path_str)
        if img_path.exists():
            try:
                # 이미지 로드 및 OCR 수행 (한국어 + 영어)
                img = Image.open(img_path)
                # Windows 환경에서 경로 문제 발생 시 주석 해제 후 수정
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                ocr_extracted_text = pytesseract.image_to_string(img, lang='kor+eng').strip()

                # OCR 추출 텍스트가 있을 경우 이미지 태그 교체
                if ocr_extracted_text:
                    # 인라인 텍스트로 깔끔하게 치환 (필요시 인용구 블록 '>' 등으로 가공 가능)
                    replacement_text = f"\n{ocr_extracted_text}\n"
                    md_text = md_text.replace(f"![]({img_path_str})", replacement_text)
                else:
                    # 텍스트가 없는 순수 그래픽인 경우 이미지 태그 제거 또는 유지를 선택
                    md_text = md_text.replace(f"![]({img_path_str})", "")

            except Exception as e:
                print(f"이미지 OCR 처리 중 오류 ({img_path_str}): {e}")

    # 4. 최종 병합된 마크다운 저장
    target_folder = Path("results")
    # 지정한 폴더가 없으면 자동 생성 (parents=True: 상위 폴더까지 생성, exist_ok=True: 이미 있어도 에러 안 냄)
    target_folder.mkdir(parents=True, exist_ok=True)

    output_path = Path(target_folder/output_md_path)
    output_path.write_text(md_text, encoding="utf-8")
    print(f"하이브리드 텍스트 병합 완료: {output_path.resolve()}")
    
    return md_text


if __name__ == "__main__":
    # 실행
    final_md = process_hybrid_ocr_with_image_text_inline("sample/sample_hybrid2.png", "final_result2.md")