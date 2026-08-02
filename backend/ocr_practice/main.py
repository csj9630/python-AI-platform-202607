from app.services.ocr_practice import OCRBenchmarkRunner

if __name__ == "__main__":
    # 실행할 테스트 이미지 지정
    IMAGE_PATH = "sample.jpg" 
    # IMAGE_PATH = "sample.pdf" 
    
    # 벤치마크 러너 객체 생성 및 실행
    runner = OCRBenchmarkRunner()
    runner.run_benchmark(IMAGE_PATH)