import os
import json
import shutil
import pickle
import argparse
import yaml
from PIL import Image
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
import time

def get_image_info_cached(image_path, cache_dict=None):
    """캐시된 이미지 정보를 반환하거나 새로 읽어서 캐시에 저장"""
    if cache_dict is not None and image_path in cache_dict:
        return cache_dict[image_path]
    
    try:
        with Image.open(image_path) as img:
            width, height = img.width, img.height
        
        if cache_dict is not None:
            cache_dict[image_path] = (width, height)
        
        return width, height
    except Exception as e:
        print(f"이미지 파일을 여는 데 실패했습니다: {image_path}. 오류: {e}")
        return None

def yolo_to_coco_bbox(yolo_bbox, img_width, img_height):
    """YOLO 형식의 바운딩 박스를 COCO 형식으로 변환"""
    x_center, y_center, w, h = yolo_bbox
    x_center *= img_width
    y_center *= img_height
    w *= img_width
    h *= img_height
    
    x_top_left = x_center - (w / 2)
    y_top_left = y_center - (h / 2)
    
    return [x_top_left, y_top_left, w, h]

def process_single_image(args):
    """단일 이미지와 레이블을 처리하는 함수 (멀티프로세싱용)"""
    image_filename, images_path, labels_path, image_id, annotation_id_start = args
    
    image_path = os.path.join(images_path, image_filename)
    
    # 이미지 정보 가져오기
    image_info = get_image_info_cached(image_path)
    if image_info is None:
        return None
    
    img_width, img_height = image_info
    
    # 이미지 정보 생성
    image_data = {
        "id": image_id,
        "width": img_width,
        "height": img_height,
        "file_name": image_filename,
        "license": 0,
        "flickr_url": "",
        "coco_url": "",
        "date_captured": 0
    }
    
    # 레이블 파일 처리
    label_filename = os.path.splitext(image_filename)[0] + '.txt'
    label_path = os.path.join(labels_path, label_filename)
    
    annotations = []
    annotation_id_counter = annotation_id_start
    
    if os.path.exists(label_path):
        try:
            with open(label_path, 'r') as f:
                for line in f.readlines():
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id, x_center, y_center, w, h = map(float, parts)
                        
                        coco_bbox = yolo_to_coco_bbox([x_center, y_center, w, h], img_width, img_height)
                        
                        annotations.append({
                            "id": annotation_id_counter,
                            "image_id": image_id,
                            "category_id": int(class_id) + 1,
                            "bbox": coco_bbox,
                            "area": coco_bbox[2] * coco_bbox[3],
                            "iscrowd": 0,
                            "segmentation": [],
                            "attributes": {"occluded": False, "rotation": 0.0}
                        })
                        annotation_id_counter += 1
        except Exception as e:
            print(f"레이블 파일 읽기 실패: {label_path}. 오류: {e}")
    
    return {
        "image": image_data,
        "annotations": annotations,
        "num_annotations": len(annotations)
    }

def copy_images_parallel(image_files, src_path, dst_path, max_workers=None):
    """이미지 파일들을 병렬로 복사"""
    def copy_single_image(image_filename):
        src_file = os.path.join(src_path, image_filename)
        dst_file = os.path.join(dst_path, image_filename)
        shutil.copy2(src_file, dst_file)
        return image_filename
    
    if max_workers is None:
        max_workers = min(32, os.cpu_count() + 4)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(tqdm(
            executor.map(copy_single_image, image_files),
            total=len(image_files),
            desc="Copying images"
        ))

def load_or_create_cache(cache_file):
    """캐시 파일을 로드하거나 새로 생성"""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except:
            print(f"캐시 파일 로드 실패: {cache_file}. 새로 생성합니다.")
    return {}

def save_cache(cache_dict, cache_file):
    """캐시를 파일로 저장"""
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_dict, f)
    except Exception as e:
        print(f"캐시 저장 실패: {e}")

def convert_yolo_to_coco_optimized(yolo_dataset_path, output_path, dataset_type, class_names, max_workers=None):
    """최적화된 YOLO to COCO 변환"""
    print(f"Converting '{dataset_type}' set with optimization...")
    
    images_path = os.path.join(yolo_dataset_path, dataset_type, 'images')
    labels_path = os.path.join(yolo_dataset_path, dataset_type, 'labels')
    
    if not os.path.exists(images_path):
        print(f"'{dataset_type}' directory not found in {yolo_dataset_path}. Skipping.")
        return
    
    # 캐시 파일 설정
    cache_file = os.path.join(yolo_dataset_path, f'.image_cache_{dataset_type}.pkl')
    image_cache = load_or_create_cache(cache_file)
    
    # COCO 출력 폴더 구조 생성
    coco_images_path = os.path.join(output_path, dataset_type)
    os.makedirs(coco_images_path, exist_ok=True)
    
    # COCO 데이터 구조 초기화
    coco_data = {
        "info": {
            "contributor": "",
            "date_created": "",
            "description": "",
            "url": "",
            "version": "",
            "year": ""
        },
        "licenses": [{"name": "", "id": 0, "url": ""}],
        "categories": [{"id": i+1, "name": name, "supercategory": ""} for i, name in enumerate(class_names)],
        "images": [],
        "annotations": []
    }
    
    # 이미지 파일 목록 가져오기
    image_files = [f for f in os.listdir(images_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"Found {len(image_files)} images")
    
    if max_workers is None:
        max_workers = min(32, os.cpu_count() + 4)
    
    # 병렬 처리를 위한 인자 준비
    annotation_id_counter = 0
    process_args = []
    
    for image_id, image_filename in enumerate(image_files):
        process_args.append((
            image_filename,
            images_path,
            labels_path,
            image_id,
            annotation_id_counter
        ))
        
        # 대략적인 annotation 수 추정 (정확하지 않지만 ID 충돌 방지용)
        label_filename = os.path.splitext(image_filename)[0] + '.txt'
        label_path = os.path.join(labels_path, label_filename)
        if os.path.exists(label_path):
            try:
                with open(label_path, 'r') as f:
                    annotation_id_counter += len(f.readlines())
            except:
                annotation_id_counter += 10  # 기본값
        
    print(f"Processing images with {max_workers} workers...")
    
    # 멀티프로세싱으로 이미지 처리
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(
            executor.map(process_single_image, process_args),
            total=len(process_args),
            desc=f"Processing {dataset_type} images"
        ))
    
    # 결과 수집
    annotation_id_counter = 0
    for result in results:
        if result is not None:
            coco_data["images"].append(result["image"])
            
            # annotation ID 재할당
            for ann in result["annotations"]:
                ann["id"] = annotation_id_counter
                annotation_id_counter += 1
                coco_data["annotations"].append(ann)
    
    # 이미지 파일 병렬 복사
    print("Copying images...")
    copy_images_parallel(image_files, images_path, coco_images_path, max_workers)
    
    # JSON 파일 저장
    coco_annotations_path = os.path.join(output_path, 'annotations')
    os.makedirs(coco_annotations_path, exist_ok=True)
    output_json_path = os.path.join(coco_annotations_path, f'instances_{dataset_type}.json')
    
    print("Saving JSON file...")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(coco_data, f, ensure_ascii=False, indent=2)
    
    # 캐시 저장
    save_cache(image_cache, cache_file)
    
    print(f"'{dataset_type}' set conversion complete!")
    print(f"  - Images: {len(coco_data['images'])}")
    print(f"  - Annotations: {len(coco_data['annotations'])}")
    print(f"  - Categories: {len(coco_data['categories'])}")
    print(f"  - Output: {output_json_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert YOLO format dataset to COCO format (Optimized).")
    parser.add_argument('--yolo_path', type=str, default='yolo', help="Path to the root directory of the YOLO dataset.")
    parser.add_argument('--coco_path', type=str, default='coco_optimized_output', help="Path to the output directory for the COCO dataset.")
    parser.add_argument('--yaml_file', type=str, default='yolo/KEPCO_OD_V7_T8_224592_AG10_2_plus_CLAHE.yaml', help='Path to the YAML file containing class names.')
    parser.add_argument('--workers', type=int, default=None, help='Number of worker processes (default: auto)')
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    # YAML 파일에서 클래스 이름 읽기
    try:
        with open(args.yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            class_names = data['names']
    except Exception as e:
        print(f"YAML 파일을 읽는 중 오류 발생: {e}")
        return
    
    print(f"Starting optimized conversion...")
    print(f"Workers: {args.workers if args.workers else 'auto'}")
    print(f"Classes: {len(class_names)}")
    
    # train, valid 세트 변환
    for dataset_type in ['train', 'valid']:
        convert_yolo_to_coco_optimized(
            args.yolo_path, 
            args.coco_path, 
            dataset_type, 
            class_names, 
            max_workers=args.workers
        )
    
    elapsed_time = time.time() - start_time
    print(f"\nTotal conversion time: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()