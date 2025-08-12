# 🔬 AI 개발 도구 모음집

YOLO / COCO Object Detection & Segmentation & Keypoint 관련 UTILS

이 저장소는 AI 모델 개발에 필요한 다양한 데이터 전처리, 변환, 그리고 웹 서비스 도구들을 포함하고 있습니다.

## 📋 목차

- [프로젝트 구조](#-프로젝트-구조)
- [1. AI 데이터셋 변환 도구](#1-ai-데이터셋-변환-도구)
- [2. AI 이미지 생성 웹 서비스](#2-ai-이미지-생성-웹-서비스)
- [3. 이미지 품질 개선 도구](#3-이미지-품질-개선-도구)
- [4. 데이터셋 구조 변환 도구](#4-데이터셋-구조-변환-도구)
- [5. YOLO 세그멘테이션 도구](#5-yolo-세그멘테이션-도구)
- [6. 데이터 포맷 변환](#6-데이터-포맷-변환)
- [7. 데이터 정리 도구](#7-데이터-정리-도구)
- [설치 방법](#-설치-방법)
- [라이센스](#-라이센스)

## 🏗️ 프로젝트 구조

```
개발중/
├── utility_ai_hpe_dataset_tools/          # AI 데이터셋 변환 도구
├── ai_image_generator_web_DATAmonitor/    # AI 이미지 생성 웹 서비스 모니터링
├── clahe_image_corrector/                 # CLAHE 이미지 보정 (단일)
├── All_images_clahe_util/                 # CLAHE 이미지 보정 (대량)
├── yolo_segmentation_tools/               # YOLO 세그멘테이션 도구
├── dataset_structure_converter.py         # 데이터셋 구조 변환
├── dataset_structure_reverter.py          # 데이터셋 구조 역변환
├── yolo_to_coco_optimized.py             # YOLO → COCO 변환
├── clean_annotations.py                  # 어노테이션 정리
└── copy_clahe_labels.py                  # 라벨 복사 도구
```

---

## 1. 🎯 AI 데이터셋 변환 도구

### 📁 위치: `utility_ai_hpe_dataset_tools/`

AI 모델 학습을 위한 데이터셋 augmentation 및 변환 도구 모음입니다.

### 🔧 주요 기능

#### 1.1 이미지 크기 조정 (`zoom_dataset.py`)

```bash
# 픽셀 크기로 리사이징
python zoom_dataset.py --input dataset_path --size 640 480

# 비율로 리사이징
python zoom_dataset.py --input dataset_path --ratio 1.5 1.5

# 출력 폴더 지정
python zoom_dataset.py --input dataset_path --output output_path --size 1024 768
```

#### 1.2 이미지 회전 (`rotate_datasets.py`)

```bash
# 45도 회전 (이미지 잘림 방지)
python rotate_datasets.py --input dataset_path --angle 45 --bound

# 90도 회전 (일반)
python rotate_datasets.py --input dataset_path --angle 90
```

#### 1.3 이미지 반전 (`flip_datasets.py`)

```bash
# 좌우 반전
python flip_datasets.py --input dataset_path

# 출력 폴더 지정
python flip_datasets.py --input dataset_path --output flipped_dataset
```

#### 1.4 HSV 색상 조정 (`hsv_datasets.py`)

```bash
# 색조, 채도, 명도 조정 (0~2 범위)
python hsv_datasets.py --input dataset_path -H 1.2 -S 1.1 -V 0.9

# 단일 값 조정
python hsv_datasets.py --input dataset_path -V 1.3  # 명도만 증가
```

#### 1.5 데이터셋 병합 (`merge_datasets.py`)

```bash
# 여러 데이터셋을 하나로 병합
python merge_datasets.py --inputs dataset1/ dataset2/ dataset3/ --output merged_dataset/
```

#### 1.6 세그멘테이션 변환 (`segmentation_transform.py`)

```bash
# 세그멘테이션 데이터 좌우 반전
python segmentation_transform.py --input dataset_path --operation flip --flip-type 1

# 세그멘테이션 데이터 회전
python segmentation_transform.py --input dataset_path --operation rotate --angle 30
```

#### 1.7 라벨 시각화 (`label_test.py`)

```python
# 키포인트 라벨 시각화
from label_test import draw_pose

IMG_PATH = 'image.jpg'
LABEL_PATH = 'label.txt'
OUTPUT_PATH = "visualized.jpg"

draw_pose(IMG_PATH, LABEL_PATH, save_path=OUTPUT_PATH)
```

### 📚 지원 데이터셋 구조

```
dataset/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
├── test/ (선택사항)
│   ├── images/
│   └── labels/
└── data.yaml
```

---

## 2. 🌐 AI 이미지 생성 웹 서비스

### 📁 위치: `ai_image_generator_web_DATAmonitor/`

외부 AI 이미지 생성 API를 활용한 웹 서비스입니다.

### 🚀 실행 방법

```bash
cd ai_image_generator_web_DATAmonitor/
python src/web_server.py
```

### 🔗 API 엔드포인트

- **메인 페이지**: `GET /`
- **헬스체크**: `GET /health`
- **API 상태 확인**: `GET /api-status`
- **설정 조회**: `GET /config`
- **이미지 생성**: `POST /create`
- **특정 API로 생성**: `POST /create/{api_name}`
- **API URL 변경**: `POST /change-api-url`

### 🛠️ 설정

`src/common/settings.py`에서 다음 설정을 변경할 수 있습니다:

- `SERVICE_PORT`: 웹 서버 포트
- `HOST`: 서버 호스트
- `EXTERNAL_API_URL`: 외부 API URL
- `API_TIMEOUT_SECONDS`: API 타임아웃

### 📦 지원 API

- **Imagen API**: 구글 Imagen 기반 이미지 생성
- 추후 DALL-E, Midjourney 등 추가 예정

---

## 3. 🖼️ 이미지 품질 개선 도구

CLAHE(Contrast Limited Adaptive Histogram Equalization)를 사용한 이미지 대비 및 명도 개선 도구입니다.

### 3.1 단일/소량 이미지 처리 (`clahe_image_corrector/`)

```bash
cd clahe_image_corrector/

# 단일 이미지 보정
python main.py image.jpg

# 출력 파일명 지정
python main.py image.jpg -o corrected_image.jpg

# 디렉토리 전체 보정
python main.py input_dir/ -d

# 파라미터 조정
python main.py image.jpg -c 2.0 -t 16 16  # clip_limit=2.0, tile_size=16x16
```

### 3.2 대량 이미지 처리 (`All_images_clahe_util/`)

```bash
cd All_images_clahe_util/

# 대량 이미지 병렬 처리
python main.py input_directory/ -d -v
```

### 🎛️ CLAHE 파라미터

- **clip_limit**: 대비 제한 임계값 (기본값: 3.0)
- **tile_grid_size**: 타일 격자 크기 (기본값: 8x8)

---

## 4. 🏗️ 데이터셋 구조 변환 도구

서로 다른 데이터셋 구조 간 변환을 지원합니다.

### 4.1 KU_SEG → Spine 구조 변환 (`dataset_structure_converter.py`)

```bash
# 기본 변환
python dataset_structure_converter.py dataset_path

# 백업 생성 후 변환
python dataset_structure_converter.py dataset_path --backup

# 검증 건너뛰기
python dataset_structure_converter.py dataset_path --verify=False
```

**변환 전 (KU_SEG 구조):**

```
dataset/
├── images/
│   ├── Train/
│   └── Validation/
└── labels/
    ├── Train/
    └── Validation/
```

**변환 후 (Spine 구조):**

```
dataset/
├── train/
│   ├── images/
│   └── labels/
└── valid/
    ├── images/
    └── labels/
```

### 4.2 Spine → KU_SEG 구조 역변환 (`dataset_structure_reverter.py`)

```bash
# 역변환
python dataset_structure_reverter.py dataset_path --backup
```

---

## 5. 🔧 YOLO 세그멘테이션 도구

### 📁 위치: `yolo_segmentation_tools/`

YOLO 세그멘테이션 데이터셋 전용 변환 도구입니다.

### 5.1 데이터셋 반전 (`flip_seg_dataset.py`)

```bash
# 좌우 반전
python flip_seg_dataset.py --input dataset_path --direction horizontal

# 상하 반전
python flip_seg_dataset.py --input dataset_path --direction vertical

# 커스텀 접미사
python flip_seg_dataset.py --input dataset_path --suffix custom_flip
```

### 5.2 데이터셋 회전 (`rotate_seg_dataset.py`)

```bash
# 30도 회전
python rotate_seg_dataset.py --input dataset_path --angle 30

# 이미지 잘림 허용
python rotate_seg_dataset.py --input dataset_path --angle 45 --no-bound
```

---

## 6. 📊 데이터 포맷 변환

### 6.1 YOLO → COCO 변환 (`yolo_to_coco_optimized.py`)

대용량 데이터셋도 빠르게 처리하는 최적화된 변환 도구입니다.

```bash
# 기본 변환
python yolo_to_coco_optimized.py --yolo_path yolo_dataset/ --coco_path coco_output/

# YAML 파일 지정
python yolo_to_coco_optimized.py --yolo_path yolo_dataset/ --yaml_file dataset.yaml

# 워커 수 지정 (병렬 처리)
python yolo_to_coco_optimized.py --yolo_path yolo_dataset/ --workers 8
```

### 🎯 최적화 특징

- **멀티프로세싱**: CPU 코어 수에 따른 자동 병렬화
- **메모리 효율**: 대용량 데이터셋 처리 최적화
- **캐싱**: 이미지 정보 캐싱으로 재처리 시간 단축
- **배치 처리**: 대량 파일 효율적 처리

---

## 7. 🧹 데이터 정리 도구

### 7.1 어노테이션 정리 (`clean_annotations.py`)

실제 존재하는 이미지에 대한 어노테이션만 남기고 정리합니다.

```bash
python clean_annotations.py
```

### 7.2 CLAHE 라벨 복사 (`copy_clahe_labels.py`)

CLAHE 처리된 이미지에 대응하는 라벨 파일을 자동 복사합니다.

```bash
python copy_clahe_labels.py
```

---

## 📦 설치 방법

### 1. 필수 라이브러리 설치

```bash
pip install opencv-python
pip install pandas numpy
pip install imutils
pip install tqdm
pip install pillow
pip install pyyaml
pip install fastapi uvicorn
pip install httpx
pip install jinja2
```

### 2. 또는 requirements.txt 사용 (생성 필요시)

```bash
pip install -r requirements.txt
```

### 3. 개별 도구 실행

각 도구는 독립적으로 실행 가능하며, 필요한 도구만 선택적으로 사용할 수 있습니다.

---

## 🎯 사용 예시

### 데이터 증강 파이프라인 예시

```bash
# 1. 원본 데이터셋 백업
cp -r original_dataset/ backup_dataset/

# 2. 이미지 품질 개선
python clahe_image_corrector/main.py original_dataset/ -d

# 3. 데이터 증강
python utility_ai_hpe_dataset_tools/flip_datasets.py --input original_dataset/
python utility_ai_hpe_dataset_tools/rotate_datasets.py --input original_dataset/ --angle 15 --bound
python utility_ai_hpe_dataset_tools/hsv_datasets.py --input original_dataset/ -V 1.2

# 4. 증강된 데이터셋 병합
python utility_ai_hpe_dataset_tools/merge_datasets.py --inputs original_dataset/ original_dataset_flip/ original_dataset_rot15/ --output final_dataset/

# 5. COCO 포맷으로 변환 (필요시)
python yolo_to_coco_optimized.py --yolo_path final_dataset/ --coco_path coco_final/
```

---

## ⚠️ 주의사항

1. **백업**: 중요한 데이터는 반드시 백업 후 작업하세요.
2. **메모리**: 대용량 데이터셋 처리 시 충분한 메모리 확보가 필요합니다.
3. **디스크 공간**: 데이터 증강 시 저장 공간이 배수로 증가합니다.
4. **파일 경로**: Windows 환경에서는 경로 구분자(`\`)에 주의하세요.

---

## 📈 성능 팁

1. **병렬 처리**: 멀티코어 시스템에서는 `--workers` 옵션을 활용하세요.
2. **SSD 사용**: 대량 파일 처리 시 SSD 사용을 권장합니다.
3. **메모리 모니터링**: 시스템 모니터로 메모리 사용량을 확인하세요.

---

## 🔧 트러블슈팅

### 자주 발생하는 문제들

1. **메모리 부족**: 배치 크기를 줄이거나 시스템 메모리를 증설하세요.
2. **파일 권한 오류**: 관리자 권한으로 실행하거나 파일 권한을 확인하세요.
3. **라이브러리 누락**: pip를 사용해 필요한 라이브러리를 설치하세요.

---
