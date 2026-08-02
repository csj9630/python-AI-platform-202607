import os
from datetime import datetime
from app.services.ocr.tesseract_ocr import TesseractOCR
from app.services.ocr.easy_ocr import EasyOCRService
from app.services.ocr.paddle_ocr import PaddleOCRService
from app.services.llm.gemini import GeminiLLM

class OCRBenchmarkRunner:
    def __init__(self):
        self.engines = [
            TesseractOCR(),
            EasyOCRService(),
            PaddleOCRService()
        ]
        self.llm = GeminiLLM()

    def run_benchmark(self, image_path: str, output_txt_path: str = "ocr_result_report.txt"):
        print("\n==================================================")
        print(f"📊 [OCR 성능 및 추출 방식 비교 벤치마크]")
        print(f"📁 대상 파일: {image_path}")
        print("==================================================\n")

        if not os.path.exists(image_path):
            print(f"❌ 에러: [{image_path}] 파일이 존재하지 않습니다.")
            return

        results = []

        # 1. OCR 3종 성능 비교 실행
        for engine in self.engines:
            print(f"🔄 [{engine.name}] 추출 실행 중...")
            res = engine.extract_text(image_path)
            results.append(res)
            
            print(f"   ⏱️ 소요 시간 : {res['elapsed_time']}초")
            print(f"   📏 추출 글자수: {len(res['text'])}자")
            print(f"   📝 추출 결과 (미리보기): {res['text'][:70].replace('\n', ' ')}...")
            print("-" * 50)

        # 2. 결과 종합 평가 및 가장 잘 추출된 결과 선택
        valid_results = [r for r in results if not r['text'].startswith("[")]
        summary_text = ""
        best_engine_name = "N/A"
        
        if valid_results:
            best_res = max(valid_results, key=lambda x: len(x['text']))
            best_engine_name = best_res['engine']
            print(f"\n💡 [최고 성능 선택]: '{best_engine_name}' (가장 많은 텍스트 추출)")
            
            # 3. Gemini 요약 연동
            print("\n🤖 [Gemini LLM 요약 진행 중...]")
            summary_text = self.llm.summarize(best_res['text'])
            
            print("\n================ [ 최종 요약 결과 ] ================")
            print(summary_text)
            print("====================================================")
        else:
            print("\n⚠️ 정상적으로 추출된 OCR 결과가 없어 요약을 진행하지 않습니다.")
            summary_text = "유효한 OCR 결과가 없어 요약이 진행되지 않았습니다."

        # 4. 비교 결과 리포트 및 추출 결과 파일 저장 (.txt)
        self._save_report_to_txt(
            image_path=image_path,
            results=results,
            best_engine_name=best_engine_name,
            summary_text=summary_text,
            output_txt_path=output_txt_path
        )

    def _save_report_to_txt(self, image_path: str, results: list, best_engine_name: str, summary_text: str, output_txt_path: str):
        """벤치마크 리포트 및 각 OCR별 전체 추출 결과를 txt 파일로 저장하는 함수"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        lines = []
        lines.append("==================================================================")
        lines.append(f"          📊 OCR 성능 비교 및 AI 요약 종합 리포트")
        lines.append("==================================================================")
        lines.append(f"■ 분석 일시     : {now}")
        lines.append(f"■ 대상 파일 경로 : {image_path}")
        lines.append(f"■ 최적 OCR 엔진  : {best_engine_name}")
        lines.append("------------------------------------------------------------------\n")

        lines.append("1. [OCR 엔진별 성능 비교 요약]")
        lines.append(f"{'엔진명':<15} | {'소요 시간(초)':<12} | {'추출 글자수(자)':<12} | {'상태':<10}")
        lines.append("-" * 60)

        for res in results:
            status = "성공" if not res['text'].startswith("[") else "실패/스킵"
            lines.append(f"{res['engine']:<15} | {res['elapsed_time']:<14.3f} | {len(res['text']):<15} | {status}")
        
        lines.append("\n" + "=" * 66)
        lines.append("2. [Gemini AI 요약 결과 (최적 추출 기준)]")
        lines.append("=" * 66)
        lines.append(summary_text)
        lines.append("\n" + "=" * 66)
        lines.append("3. [각 OCR 엔진별 추출 결과 전체 원문]")
        lines.append("=" * 66 + "\n")

        for res in results:
            lines.append(f"▶ [{res['engine']}] 추출 원문 전체 (소요시간: {res['elapsed_time']}s / 글자수: {len(res['text'])}자)")
            lines.append("-" * 66)
            lines.append(res['text'] if res['text'] else "(추출된 내용이 없습니다.)")
            lines.append("\n" + "=" * 66 + "\n")

        # 파일 쓰기 (UTF-8 인코딩)
        try:
            with open(output_txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"\n📄 [성공] 비교 결과 리포트가 성공적으로 저장되었습니다 ➔ {output_txt_path}")
        except Exception as e:
            print(f"\n❌ [오류] TXT 리포트 저장 실패: {e}")