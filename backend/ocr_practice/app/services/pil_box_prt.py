import easyocr
from PIL import Image, ImageDraw

reader = easyocr.Reader(['ko', 'en'])
img = 'sample3.png'

# OCR 실행 (좌표, 텍스트, 신뢰도 점수가 같이 나옴)
results = reader.readtext(img)

# PIL 이미지 로드
image = Image.open(img)
draw = ImageDraw.Draw(image)

for bbox, text, prob in results:
    # prob: 신뢰도(0~1). 신뢰도가 낮은 것은 전처리로 걸러낼 수 있음!
    # if prob < 0.5:
    #     continue

    # bbox 좌표: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    p0, p1, p2, p3 = bbox
    
    # 1. PIL로 네모 상자 그리기 (시각화)
    draw.rectangle([p0[0], p0[1], p2[0], p2[1]], outline="red", width=2)
    
    # 2. y 좌표 기준으로 줄 바꿈/위치 정렬 기준 세우기
    print(f"텍스트: {text} | Y위치: {p0[1]} | 신뢰도: {prob:.2f}")

# 박스가 그려진 이미지 저장 (React 프론트에 전달 가능)
image.save('result_bbox.png')