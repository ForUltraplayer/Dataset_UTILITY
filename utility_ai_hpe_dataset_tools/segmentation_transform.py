import cv2
import pandas as pd
import os
import numpy as np
import utils
import const
from math import cos, sin, radians
import imutils

def parse_polygon_coordinates(label_line):
    """
    segmentation 라벨에서 polygon 좌표를 파싱
    
    :param label_line: 라벨 파일의 한 줄 (class_id x1 y1 x2 y2 ... xn yn)
    :return: (class_id, polygon_coords)
    """
    coords = list(map(float, label_line.strip().split()))
    class_id = int(coords[0])
    polygon_coords = np.array(coords[1:]).reshape(-1, 2)
    return class_id, polygon_coords

def format_polygon_coordinates(class_id, polygon_coords):
    """
    polygon 좌표를 YOLO segmentation 형식으로 변환
    
    :param class_id: 클래스 ID
    :param polygon_coords: polygon 좌표 배열 [(x1,y1), (x2,y2), ...]
    :return: 포맷된 문자열
    """
    coord_str = ' '.join([f"{x:.6f} {y:.6f}" for x, y in polygon_coords])
    return f"{class_id} {coord_str}"

def flip_polygon_coordinates(polygon_coords, image_width, flip_type=1):
    """
    polygon 좌표를 좌우반전 또는 상하반전
    
    :param polygon_coords: polygon 좌표 배열 [(x1,y1), (x2,y2), ...]
    :param image_width: 이미지 너비 (normalized 좌표의 경우 1.0)
    :param flip_type: 0=상하반전, 1=좌우반전
    :return: 변환된 polygon 좌표
    """
    flipped_coords = polygon_coords.copy()
    
    if flip_type == 1:  # 좌우반전
        flipped_coords[:, 0] = 1.0 - flipped_coords[:, 0]
    else:  # 상하반전
        flipped_coords[:, 1] = 1.0 - flipped_coords[:, 1]
    
    return flipped_coords

def rotate_polygon_coordinates(polygon_coords, angle, image_size):
    """
    polygon 좌표를 회전
    
    :param polygon_coords: normalized polygon 좌표 배열 [(x1,y1), (x2,y2), ...]
    :param angle: 회전각 (반시계방향, 도)
    :param image_size: (height, width) 
    :return: 회전된 polygon 좌표
    """
    h, w = image_size
    
    # normalized -> pixel 좌표로 변환
    pixel_coords = polygon_coords.copy()
    pixel_coords[:, 0] *= w
    pixel_coords[:, 1] *= h
    
    # 회전 중심 (이미지 중앙)
    cx, cy = w / 2.0, h / 2.0
    
    # 회전 각도를 라디안으로 변환
    rad = radians(angle)
    
    # 회전 변환
    rotated_coords = np.zeros_like(pixel_coords)
    for i, (x, y) in enumerate(pixel_coords):
        # 중심을 원점으로 이동
        x_centered = x - cx
        y_centered = y - cy
        
        # 회전 변환
        x_rot = x_centered * cos(rad) - y_centered * sin(rad)
        y_rot = x_centered * sin(rad) + y_centered * cos(rad)
        
        # 중심을 다시 이동
        rotated_coords[i] = [x_rot + cx, y_rot + cy]
    
    # pixel -> normalized 좌표로 변환
    rotated_coords[:, 0] /= w
    rotated_coords[:, 1] /= h
    
    # 좌표를 0-1 범위로 클리핑
    rotated_coords = np.clip(rotated_coords, 0.0, 1.0)
    
    return rotated_coords

def rotate_polygon_with_bound(polygon_coords, angle, original_size, rotated_size):
    """
    이미지 회전 시 크기 변경을 고려한 polygon 좌표 회전
    
    :param polygon_coords: normalized polygon 좌표 배열
    :param angle: 회전각 (반시계방향, 도)
    :param original_size: 원본 이미지 크기 (height, width)
    :param rotated_size: 회전 후 이미지 크기 (height, width)
    :return: 회전된 polygon 좌표
    """
    orig_h, orig_w = original_size
    rot_h, rot_w = rotated_size
    
    # normalized -> 원본 pixel 좌표로 변환
    pixel_coords = polygon_coords.copy()
    pixel_coords[:, 0] *= orig_w
    pixel_coords[:, 1] *= orig_h
    
    # 원본 이미지 중심
    orig_cx, orig_cy = orig_w / 2.0, orig_h / 2.0
    
    # 회전된 이미지의 중심 (크기 변경으로 인한 오프셋 고려)
    rot_cx = rot_w / 2.0
    rot_cy = rot_h / 2.0
    
    # 회전 각도를 라디안으로 변환
    rad = radians(angle)
    
    # 회전 변환
    rotated_coords = np.zeros_like(pixel_coords)
    for i, (x, y) in enumerate(pixel_coords):
        # 원본 이미지 중심을 원점으로 이동
        x_centered = x - orig_cx
        y_centered = y - orig_cy
        
        # 회전 변환
        x_rot = x_centered * cos(rad) - y_centered * sin(rad)
        y_rot = x_centered * sin(rad) + y_centered * cos(rad)
        
        # 회전된 이미지의 중심으로 이동
        rotated_coords[i] = [x_rot + rot_cx, y_rot + rot_cy]
    
    # pixel -> normalized 좌표로 변환 (회전된 이미지 크기 기준)
    rotated_coords[:, 0] /= rot_w
    rotated_coords[:, 1] /= rot_h
    
    # 좌표를 0-1 범위로 클리핑
    rotated_coords = np.clip(rotated_coords, 0.0, 1.0)
    
    return rotated_coords

def flip_segmentation_dataset(image_path, label_path, flip_type=1):
    """
    segmentation 데이터셋 좌우반전/상하반전
    
    :param image_path: 이미지 파일 경로
    :param label_path: 라벨 파일 경로
    :param flip_type: 0=상하반전, 1=좌우반전
    :return: (flipped_image, flipped_labels)
    """
    # 이미지 로드 및 변환
    input_image = cv2.imread(image_path)
    flipped_image = cv2.flip(input_image, flip_type)
    
    flipped_labels = []
    
    try:
        # 라벨 파일 읽기
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if line.strip():
                class_id, polygon_coords = parse_polygon_coordinates(line)
                flipped_coords = flip_polygon_coordinates(polygon_coords, 1.0, flip_type)
                flipped_labels.append(format_polygon_coordinates(class_id, flipped_coords))
                
    except FileNotFoundError:
        # 라벨 파일이 없는 경우
        pass
    except Exception as e:
        print(f"Error processing {label_path}: {e}")
        
    return flipped_image, flipped_labels

def rotate_segmentation_dataset(image_path, label_path, angle, use_bound=True):
    """
    segmentation 데이터셋 회전
    
    :param image_path: 이미지 파일 경로
    :param label_path: 라벨 파일 경로
    :param angle: 회전각 (반시계방향, 도)
    :param use_bound: True면 이미지 잘림 방지
    :return: (rotated_image, rotated_labels)
    """
    # 이미지 로드
    input_image = cv2.imread(image_path)
    original_size = input_image.shape[:2]  # (height, width)
    
    # 이미지 회전
    if angle % 360 == 0:
        rotated_image = input_image
        rotated_size = original_size
    else:
        if use_bound:
            rotated_image = imutils.rotate_bound(input_image, -angle)  # imutils는 시계방향이므로 -angle
        else:
            rotated_image = imutils.rotate(input_image, -angle)
        rotated_size = rotated_image.shape[:2]
    
    rotated_labels = []
    
    try:
        # 라벨 파일 읽기
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if line.strip():
                class_id, polygon_coords = parse_polygon_coordinates(line)
                
                if angle % 360 == 0:
                    rotated_coords = polygon_coords
                elif use_bound:
                    rotated_coords = rotate_polygon_with_bound(polygon_coords, angle, original_size, rotated_size)
                else:
                    rotated_coords = rotate_polygon_coordinates(polygon_coords, angle, original_size)
                
                rotated_labels.append(format_polygon_coordinates(class_id, rotated_coords))
                
    except FileNotFoundError:
        # 라벨 파일이 없는 경우
        pass
    except Exception as e:
        print(f"Error processing {label_path}: {e}")
        
    return rotated_image, rotated_labels

def save_segmentation_labels(output_path, labels):
    """
    segmentation 라벨을 파일로 저장
    
    :param output_path: 저장할 파일 경로
    :param labels: 라벨 리스트
    """
    with open(output_path, 'w') as f:
        for label in labels:
            f.write(label + '\n')

def process_flip_dataset(input_dataset, output_dataset='', flip_type=1):
    """
    전체 데이터셋에 대해 좌우반전/상하반전 처리
    
    :param input_dataset: 입력 데이터셋 경로
    :param output_dataset: 출력 데이터셋 경로
    :param flip_type: 0=상하반전, 1=좌우반전
    """
    _SUFFIX = "flip"
    TEXT_EXT = ".txt"
    
    folder_list = [const.VALID_FOLDER_NAME, const.TRAIN_FOLDER_NAME]
    
    if output_dataset == '':
        output_dataset = f'{input_dataset}_{_SUFFIX}'
    
    if const.TEST_FOLDER_NAME in os.listdir(input_dataset):
        folder_list = [const.TEST_FOLDER_NAME, const.VALID_FOLDER_NAME, const.TRAIN_FOLDER_NAME]
    
    for folder in folder_list:
        # 폴더 경로 설정
        input_images_folder = os.path.join(input_dataset, folder, const.IMAGES_FOLDER_NAME)
        input_labels_folder = os.path.join(input_dataset, folder, const.LABELS_FOLDER_NAME)
        
        output_images_folder = os.path.join(output_dataset, folder, const.IMAGES_FOLDER_NAME)
        output_labels_folder = os.path.join(output_dataset, folder, const.LABELS_FOLDER_NAME)
        
        # 출력 폴더 생성
        utils.directory_check(output_images_folder)
        utils.directory_check(output_labels_folder)
        
        if not os.path.exists(input_images_folder):
            continue
            
        # 각 이미지 파일 처리
        for image_file in os.listdir(input_images_folder):
            file_name, image_ext = os.path.splitext(image_file)
            
            input_image_path = os.path.join(input_images_folder, f'{file_name}{image_ext}')
            input_label_path = os.path.join(input_labels_folder, f'{file_name}{TEXT_EXT}')
            
            output_image_path = os.path.join(output_images_folder, f'{file_name}_{_SUFFIX}{image_ext}')
            output_label_path = os.path.join(output_labels_folder, f'{file_name}_{_SUFFIX}{TEXT_EXT}')
            
            # 변환 처리
            flipped_image, flipped_labels = flip_segmentation_dataset(input_image_path, input_label_path, flip_type)
            
            # 결과 저장
            utils.save_images(output_image_path, flipped_image)
            save_segmentation_labels(output_label_path, flipped_labels)
            
            print(f"Processed: {image_file}")
    
    # YAML 파일 복사
    utils.copy_yaml(input_dataset, output_dataset)

def process_rotate_dataset(input_dataset, angle, use_bound=True, output_dataset=''):
    """
    전체 데이터셋에 대해 회전 처리
    
    :param input_dataset: 입력 데이터셋 경로
    :param angle: 회전각 (반시계방향, 도)
    :param use_bound: True면 이미지 잘림 방지
    :param output_dataset: 출력 데이터셋 경로
    """
    _SUFFIX = f"rot_{angle}"
    TEXT_EXT = ".txt"
    
    folder_list = [const.VALID_FOLDER_NAME, const.TRAIN_FOLDER_NAME]
    
    if output_dataset == '':
        output_dataset = f'{input_dataset}_rot{angle}'
    
    if const.TEST_FOLDER_NAME in os.listdir(input_dataset):
        folder_list = [const.TEST_FOLDER_NAME, const.VALID_FOLDER_NAME, const.TRAIN_FOLDER_NAME]
    
    for folder in folder_list:
        # 폴더 경로 설정
        input_images_folder = os.path.join(input_dataset, folder, const.IMAGES_FOLDER_NAME)
        input_labels_folder = os.path.join(input_dataset, folder, const.LABELS_FOLDER_NAME)
        
        output_images_folder = os.path.join(output_dataset, folder, const.IMAGES_FOLDER_NAME)
        output_labels_folder = os.path.join(output_dataset, folder, const.LABELS_FOLDER_NAME)
        
        # 출력 폴더 생성
        utils.directory_check(output_images_folder)
        utils.directory_check(output_labels_folder)
        
        if not os.path.exists(input_images_folder):
            continue
            
        # 각 이미지 파일 처리
        for image_file in os.listdir(input_images_folder):
            file_name, image_ext = os.path.splitext(image_file)
            
            input_image_path = os.path.join(input_images_folder, f'{file_name}{image_ext}')
            input_label_path = os.path.join(input_labels_folder, f'{file_name}{TEXT_EXT}')
            
            output_image_path = os.path.join(output_images_folder, f'{file_name}_{_SUFFIX}{image_ext}')
            output_label_path = os.path.join(output_labels_folder, f'{file_name}_{_SUFFIX}{TEXT_EXT}')
            
            # 변환 처리
            rotated_image, rotated_labels = rotate_segmentation_dataset(input_image_path, input_label_path, angle, use_bound)
            
            # 결과 저장
            utils.save_images(output_image_path, rotated_image)
            save_segmentation_labels(output_label_path, rotated_labels)
            
            print(f"Processed: {image_file}")
    
    # YAML 파일 복사
    utils.copy_yaml(input_dataset, output_dataset)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Segmentation dataset transformation tool")
    parser.add_argument('--input', type=str, required=True, help="입력 데이터셋 폴더")
    parser.add_argument('--operation', type=str, required=True, choices=['flip', 'rotate'], help="변환 작업 (flip 또는 rotate)")
    parser.add_argument('--output', type=str, required=False, default="", help="출력 데이터셋 폴더")
    
    # flip 관련 옵션
    parser.add_argument('--flip-type', type=int, default=1, choices=[0, 1], help="반전 타입 (0: 상하반전, 1: 좌우반전)")
    
    # rotate 관련 옵션
    parser.add_argument('--angle', type=float, default=0, help="회전각 (반시계방향, 도)")
    parser.add_argument('--no-bound', action='store_true', help="이미지 잘림 방지 안함")
    
    args = parser.parse_args()
    
    if args.operation == 'flip':
        process_flip_dataset(args.input, args.output, args.flip_type)
    elif args.operation == 'rotate':
        process_rotate_dataset(args.input, args.angle, not args.no_bound, args.output)