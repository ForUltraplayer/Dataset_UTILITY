import cv2
import numpy as np

def draw_pose(image_path, keypoint_txt_path, visible=0, save_path='output.jpg'):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")

    h, w = img.shape[:2]

    with open(keypoint_txt_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        nums = list(map(float, line.strip().split()))
        if len(nums) <= 5:
            continue

        cls, cx, cy, bw, bh = nums[:5]
        keypoints = np.array(nums[5:]).reshape(-1, 3)

        # 🔲 bbox 시각화
        x1 = int((cx - bw / 2) * w)
        y1 = int((cy - bh / 2) * h)
        x2 = int((cx + bw / 2) * w)
        y2 = int((cy + bh / 2) * h)

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 빨간색 bbox
        cv2.putText(img, f'cls:{int(cls)}', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # 🔘 keypoint 시각화
        for i, (x_rel, y_rel, v) in enumerate(keypoints):
            if v >= visible:
                x = int(x_rel * w)
                y = int(y_rel * h)
                cv2.circle(img, (x, y), 4, (0, 255, 0), -1)
                cv2.putText(img, str(i), (x + 4, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    cv2.imwrite(save_path, img)
    print(f"✅ 시각화 저장 완료: {save_path}")

# 실행 예시
"""
LABEL_PATH 의 라벨 형태는 yolo 형태
"""
IMG_PATH = 'aa.jpg'
LABEL_PATH = 'aa.txt'
OUTPUT_PATH = "VIS_a.jpg"

draw_pose(IMG_PATH, LABEL_PATH, save_path=OUTPUT_PATH)