from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseOCR(ABC):
    """모든 OCR 엔진이 따라야 하는 표준 인터페이스"""
    
    @abstractmethod
    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        이미지 경로를 받아 텍스트, 소요시간, 엔진 이름을 반환
        반환 예시: {'engine': 'Tesseract', 'text': '...', 'elapsed_time': 1.23}
        """
        pass