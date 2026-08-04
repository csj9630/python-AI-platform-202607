import pymupdf4llm
import pathlib

def convert_pdf_to_markdown(pdf_path: str, output_md_path: str):
    """
    PDF를 분석하여 텍스트와 이미지(OCR)를 병합한 Markdown 파일로 변환합니다.
    """
    print(f"'{pdf_path}' 변환 시작...")
    
    # to_markdown 함수가 하이브리드 추출 및 레이아웃 병합을 모두 자동 처리합니다.
    md_text = pymupdf4llm.to_markdown(
        doc=pdf_path,
        write_images=True,          # 문서 내 이미지 영역을 실제 이미지 파일로 추출할지 여부
        image_path="output_images", # 추출된 이미지가 저장될 디렉토리 경로
        image_format="png",         # 추출 이미지 포맷
        dpi=300                     # OCR 및 이미지 추출 해상도
    )
    
    # 추출된 마크다운 텍스트를 파일로 저장
    output_file = pathlib.Path(output_md_path)
    output_file.write_bytes(md_text.encode("utf-8"))
    
    print(f"변환 완료! 결과가 '{output_md_path}'에 저장되었습니다.")

# 실행 예시
if __name__ == "__main__":
    convert_pdf_to_markdown("sample_hybrid2.png", "result.md")
    # convert_pdf_to_markdown("hybrid_sample.pdf", "result.md")