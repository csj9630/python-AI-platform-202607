import sys
from ocr import extract_text
from gemini import summarize_text

def run_pipeline(image_path: str):
    print("==================================================")
    print(f"📷 1. 이미지 읽기 및 OCR 텍스트 추출 중... [{image_path}]")
    
    try:
        # 1. OCR 실행
        ocr_result = extract_text(image_path)
        print("\n[OCR 추출 텍스트 원문]")
        print("--------------------------------------------------")
        print(ocr_result if ocr_result else "(인식된 텍스트가 없습니다.)")
        print("--------------------------------------------------")

        if not ocr_result:
            print("⚠️ 추출된 텍스트가 없어 요약을 진행하지 않습니다.")
            return

        # 2. Gemini 요약 실행
        print("\n🤖 2. Gemini API 호출 및 요약 진행 중...")
        summary_result = summarize_text(ocr_result)

        print("\n================ [ 최종 AI 요약 결과 ] ================")
        print(summary_result)
        print("========================================================")

    except Exception as e:
        print(f"\n❌ 파이프라인 실행 중 에러 발생: {e}")

if __name__ == "__main__":
    # 실행할 이미지 파일명 (프로젝트 루트 경로에 sample.jpg 준비)
    target_image = "sample.jpg"
    
    # 실행 시 인자로 이미지 경로를 전달할 수도 있음 (python main.py my_doc.png)
    if len(sys.argv) > 1:
        target_image = sys.argv[1]

    run_pipeline(target_image)