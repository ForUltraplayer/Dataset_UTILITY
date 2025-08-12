#!/usr/bin/env python3
import json
import os
from pathlib import Path

def get_image_files(image_dir):
    """디렉토리에서 이미지 파일명들을 가져와서 이미지 ID 세트로 반환"""
    image_files = set()
    if os.path.exists(image_dir):
        for file in os.listdir(image_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # 파일명에서 이미지 ID 추출 (예: 000000581482.jpg -> 581482)
                image_id = int(file.split('.')[0])
                image_files.add(image_id)
    return image_files

def clean_coco_json(json_path, valid_image_ids, output_path):
    """COCO JSON 파일을 정리하여 실제 존재하는 이미지에 대한 데이터만 포함시킴"""
    print(f"처리 중: {json_path}...")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_images = len(data.get('images', []))
    original_annotations = len(data.get('annotations', []))
    
    # 이미지 필터링
    filtered_images = []
    valid_image_ids_in_json = set()
    
    for img in data.get('images', []):
        if img['id'] in valid_image_ids:
            filtered_images.append(img)
            valid_image_ids_in_json.add(img['id'])
    
    # 어노테이션 필터링 (유효한 이미지에 대한 어노테이션만 유지)
    filtered_annotations = []
    for ann in data.get('annotations', []):
        if ann['image_id'] in valid_image_ids_in_json:
            filtered_annotations.append(ann)
    
    # 데이터 업데이트
    data['images'] = filtered_images
    data['annotations'] = filtered_annotations
    
    # 정리된 JSON 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'))
    
    print(f"  원본: {original_images}개 이미지, {original_annotations}개 어노테이션")
    print(f"  필터링 후: {len(filtered_images)}개 이미지, {len(filtered_annotations)}개 어노테이션")
    print(f"  정리된 파일 저장: {output_path}")

def main():
    base_dir = Path(__file__).parent
    
    # train2017, val2017 폴더에서 유효한 이미지 ID들 가져오기
    train_images = get_image_files(base_dir / 'train2017')
    val_images = get_image_files(base_dir / 'val2017')
    
    print(f"train2017/에서 {len(train_images)}개 이미지 발견")
    print(f"val2017/에서 {len(val_images)}개 이미지 발견")
    
    # train 어노테이션 정리
    train_json = base_dir / 'annotations' / 'instances_train2017.json'
    if train_json.exists():
        clean_coco_json(
            train_json, 
            train_images, 
            base_dir / 'annotations' / 'instances_train2017_cleaned.json'
        )
    
    # val 어노테이션 정리
    val_json = base_dir / 'annotations' / 'instances_val2017.json'
    if val_json.exists():
        clean_coco_json(
            val_json, 
            val_images, 
            base_dir / 'annotations' / 'instances_val2017_cleaned.json'
        )
    
    print("정리 완료!")

if __name__ == '__main__':
    main()