# UTILITY_AI_HPE_DATASET_TOOLS

YOLO HPE dataset 관련 tool 모음 (필요시 추가)

### dataset 이미지 좌우 반전

이미지들을 좌우 반전 및 라벨링 좌표 변환

```commandline
python flip_datasets.py [--input input path] [--output output path]
```
- --input: 입력 데이터셋 경로
- --output: 처리 후 결과 파일을 저장할 경로 ( default: same as source path )

<br>

### dataset 이미지 회전

이미지들을 회전하고 라벨링 좌표 재계산

```commandline
python rotate_datasets.py [--input input path] [--output output path] [--angle angle] [--bound]
```
- --input: 입력 데이터셋 경로
- --output: 처리 후 결과 파일을 저장할 경로 ( default: same as source path )
- --angle: 이동하기를 원하는 각도 
- --bound: 이미지 회전시 이미지 잘림 여부 ( default: False )

<br>

### dataset 리사이즈

이미지의 사이즈, 좌표 조정

```commandline
python zoom_dataset.py [--input input path] [--output output path] [--size Xs Ys] [--ratio Xr Yr]
```
- --input: 입력 데이터셋 경로
- --output: 처리 후 결과 파일을 저장할 경로 ( default: same as source path )
- --size: 고정사이즈로 리사이징 ( default: null )
- --ratio: 비율로 리사이징 ( default: null )

<br>

### dataset hsv 좌표계로 조정

이미지의 색감 조절

```commandline
python hsv_dataset.py [--input input path] [--output output path] [-H --hue hue] [-S --saturation saturation] [-V --value value]
```
- --input: 입력 데이터셋 경로
- --output: 처리 후 결과 파일을 저장할 경로 ( default: same as source path )
- -H, --hue: 색조, 원본 이미지 대비 배수 0~2 사이 값
- -S, --saturation : 채도, 원본 이미지 대비 배수 0~2 사이 값
- -V, --value : 명도, 원본 이미지 대비 배수 0~2 사이 값
<br>