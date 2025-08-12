# YOLO Segmentation Dataset Tools

YOLO segmentation 데이터셋을 위한 이미지 변환 도구 모음입니다. 이미지와 polygon 라벨을 함께 변환하여 데이터 증강을 수행할 수 있습니다.

## 기능

- **Flip (좌우/상하 반전)**: 이미지와 polygon 좌표를 함께 반전
- **Rotate (회전)**: 지정된 각도로 이미지와 polygon 좌표를 함께 회전

## 설치

### 요구사항
```bash
pip install -r requirements.txt
```

필요한 패키지:
- opencv-python >= 4.5.0
- numpy >= 1.19.0
- tqdm >= 4.62.0

## 데이터셋 구조

지원되는 YOLO 데이터셋 구조:
```
dataset/
├── data.yaml
├── train/
│   ├── images/
│   │   ├── image1.jpg
│   │   └── image2.jpg
│   └── labels/
│       ├── image1.txt
│       └── image2.txt
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

### 라벨 포맷
YOLO segmentation 포맷 (normalized polygon coordinates):
```
class_id x1 y1 x2 y2 x3 y3 ... xn yn
```

## 사용법

### 1. Dataset Flip (좌우/상하 반전)

```bash
# 좌우 반전 (기본값)
python flip_seg_dataset.py --input /path/to/dataset --output /path/to/output

# 상하 반전
python flip_seg_dataset.py --input /path/to/dataset --output /path/to/output --direction vertical

# 출력 경로 생략 시 자동 생성
python flip_seg_dataset.py --input /path/to/dataset --direction horizontal
```

#### 옵션
- `--input`: 입력 데이터셋 경로 (필수)
- `--output`: 출력 데이터셋 경로 (선택, 기본값: input_path_flip_h 또는 input_path_flip_v)
- `--direction`: 반전 방향 (`horizontal` 또는 `vertical`, 기본값: `horizontal`)
- `--suffix`: 출력 파일명에 추가할 접미사 (선택, 기본값: `flip_h` 또는 `flip_v`)

### 2. Dataset Rotate (회전)

```bash
# 90도 회전 (캔버스 크기 유지)
python rotate_seg_dataset.py --input /path/to/dataset --output /path/to/output --angle 90

# 45도 회전 (캔버스 확장하여 잘림 방지)
python rotate_seg_dataset.py --input /path/to/dataset --output /path/to/output --angle 45 --expand

# 출력 경로 생략 시 자동 생성
python rotate_seg_dataset.py --input /path/to/dataset --angle 180
```

#### 옵션
- `--input`: 입력 데이터셋 경로 (필수)
- `--output`: 출력 데이터셋 경로 (선택, 기본값: input_path_rot_ANGLE 또는 input_path_rot_ANGLE_exp)
- `--angle`: 회전 각도 (필수, 양수 = 반시계방향)
- `--expand`: 캔버스 확장으로 잘림 방지 (선택)
- `--suffix`: 출력 파일명에 추가할 접미사 (선택)

## 사용 예시

### KU_SEG_266 데이터셋 처리

```bash
# 1. 좌우 반전
python flip_seg_dataset.py --input KU_SEG_266_V1_T1_clahe --direction horizontal

# 2. 90도 회전 (캔버스 확장)
python rotate_seg_dataset.py --input KU_SEG_266_V1_T1_clahe --angle 90 --expand

# 3. 45도 회전
python rotate_seg_dataset.py --input KU_SEG_266_V1_T1_clahe --angle 45 --expand
```

## 주요 특징

### Flip 변환
- **수평 반전**: `x' = 1 - x` (y 좌표 유지)
- **수직 반전**: `y' = 1 - y` (x 좌표 유지)
- Polygon의 모든 점에 대해 변환 적용

### Rotate 변환
- 이미지 중심 (0.5, 0.5)을 기준으로 회전
- **일반 회전**: 원본 이미지 크기 유지 (모서리 잘림 가능)
- **확장 회전** (`--expand`): 캔버스 크기를 확장하여 잘림 방지
- Rotation matrix를 사용한 정확한 좌표 변환

### 데이터 검증
- 변환 후 유효하지 않은 polygon 자동 필터링
- 최소 면적 임계값 적용 (기본값: 0.001)
- 3개 미만의 점을 가진 polygon 제거

## 출력 파일

변환된 데이터셋은 원본과 동일한 구조로 출력됩니다:
- 이미지와 라벨 파일에 접미사 추가 (예: `image1_flip_h.jpg`, `image1_flip_h.txt`)
- `data.yaml` 파일 자동 복사
- 원본 데이터셋의 train/valid/test 구조 유지

## 참고사항

1. **좌표계**: YOLO 정규화 좌표 (0~1 범위) 사용
2. **이미지 포맷**: JPG, JPEG, PNG, BMP 지원
3. **메모리**: 대용량 데이터셋의 경우 배치 처리로 메모리 사용량 최적화
4. **에러 처리**: 개별 파일 처리 실패 시에도 전체 작업 계속 진행

## 라이센스

MIT License

## 기여

버그 리포트나 기능 제안은 Issues를 통해 제출해 주세요.