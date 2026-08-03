from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

def preprocess_for_ocr(image_path):
    img = Image.open(image_path)
    
    # 1. 흑백(Grayscale) 변환
    img = img.convert('L')
    
    # 2. 선명도(Sharpness) 및 대비(Contrast) 향상
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # 대비 2배 강화
    
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)  # 글자 경계선 선명화
    
    return img



def apply_thresholding(image_path):
    # OpenCV로 이미지 로드 (그레이스케일)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # 적응형 이진화 (Adaptive Thresholding) - 조명이 불균일한 문서에 최적
    binary_img = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # 자잘한 점 노이즈 제거 (Morphology Operation)
    kernel = np.ones((1, 1), np.uint8)
    clean_img = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, kernel)
    
    return clean_img