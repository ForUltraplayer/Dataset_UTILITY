# CLAHE Image Corrector

CLAHE(Contrast Limited Adaptive Histogram Equalization)를 사용한 이미지 대비 및 명도 보정 도구입니다.

## 기능

- 단일 이미지 보정
- 디렉토리 내 전체 이미지 일괄 보정
- CLAHE 파라미터 커스터마이징
- 다양한 이미지 포맷 지원 (JPG, PNG, BMP, TIFF 등)

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 기본 사용법

```bash
# 단일 이미지 보정
python main.py input_image.jpg

# 출력 파일명 지정
python main.py input_image.jpg -o output_image.jpg

# 디렉토리 전체 보정
python main.py input_directory/ -d

# 출력 디렉토리 지정
python main.py input_directory/ -d -o output_directory/
```

### 고급 옵션

```bash
# CLAHE 파라미터 조정
python main.py image.jpg -c 2.0 -t 16 16

# 특정 확장자만 처리 (디렉토리 모드)
python main.py input_dir/ -d -e .jpg .png

# 상세 출력 모드
python main.py image.jpg -v
```

## 파라미터 설명

- `-c, --clip-limit`: 대비 제한 임계값 (기본값: 3.0)
  - 값이 클수록 더 강한 대비 향상
  - 권장 범위: 1.0 ~ 5.0

- `-t, --tile-size`: 타일 격자 크기 (기본값: 8 8)
  - 작은 값: 더 세밀한 국소 보정
  - 큰 값: 더 넓은 영역의 전역 보정
  - 권장 범위: 4x4 ~ 16x16

## CLAHE란?

CLAHE(Contrast Limited Adaptive Histogram Equalization)는 이미지의 국소적 대비를 향상시키는 기법입니다.

### 장점
- 역광이나 불균등한 조명 상황에서 효과적
- 과도한 대비 증가를 방지하는 제한 기능
- 이미지의 세부사항을 보존하면서 가시성 향상

### 적용 사례
- 의료 영상 개선
- 감시 카메라 영상 보정
- 저조도 사진 개선
- 역광 사진 보정

## 프로젝트 구조

```
clahe_image_corrector/
├── main.py              # 메인 실행 스크립트
├── src/
│   └── corrector.py     # CLAHE 보정 클래스
├── requirements.txt     # 의존성 패키지
└── README.md           # 이 파일
```

## 예시

### 보정 전/후 비교

원본 이미지가 어둡거나 대비가 낮은 경우:
```bash
python main.py dark_image.jpg -o bright_image.jpg
```

여러 이미지를 한번에 처리:
```bash
python main.py photos/ -d -o corrected_photos/
```

### 파라미터 실험

약한 보정:
```bash
python main.py image.jpg -c 1.5 -t 4 4 -o mild_correction.jpg
```

강한 보정:
```bash
python main.py image.jpg -c 4.0 -t 16 16 -o strong_correction.jpg
```

## 지원 파일 형식

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- 기타 OpenCV에서 지원하는 형식

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.