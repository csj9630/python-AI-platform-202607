import fitz  # PyMuPDF
import pymupdf4llm
from pathlib import Path

def process_hybrid_pdf_ocr(pdf_path: str, output_md_path: str = "output.md") -> str:
    """
    디지털 텍스트, 글꼴, 레이아웃을 보존하면서 
    텍스트 누락 영역(이미지/스캔본)만 선택적으로 OCR 처리하여 Markdown으로 변환합니다.
    """
    doc_path = Path(pdf_path)
    if not doc_path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {pdf_path}")

    # 1. 문서 검증 및 사전 체크
    with fitz.open(doc_path) as doc:
        print(f"문서 로드 완료: 총 {len(doc)} 페이지")

    # 2. pymupdf4llm을 활용한 선택적 OCR 및 레이아웃 유지 추출
    # to_markdown은 기본적으로 내장 디지털 텍스트와 좌표를 우선 사용하고,
    # 텍스트가 누락되거나 없는 이미지 영역만 OCR을 가동해 레이아웃에 맞춰 병합합니다.
    markdown_result = pymupdf4llm.to_markdown(
        doc=str(doc_path),
        page_chunks=False,         # 전체 문서를 하나의 마크다운 텍스트로 결합
        write_images=True,         # 누락 영역의 이미지/도표를 추출하여 저장
        image_path="extracted_img",# 이미지 저장 폴더 지정
        image_format="png",        # 추출 이미지 포맷
        dpi=300                    # OCR 고해상도 처리
    )

    # 3. 추출된 결과 저장
    output_path = Path(output_md_path)
    output_path.write_text(markdown_result, encoding="utf-8")
    
    print(f"하이브리드 OCR 처리 완료: {output_path.resolve()}")
    return markdown_result


if __name__ == "__main__":
    # 실행 테스트
    sample_pdf = "hybrid_sample.pdf"
    
    try:
        md_text = process_hybrid_pdf_ocr(sample_pdf, "hybrid_result.md")
        print("\n--- 추출 결과 미리보기 ---")
        print(md_text[:500])
    except Exception as e:
        print(f"오류 발생: {e}")