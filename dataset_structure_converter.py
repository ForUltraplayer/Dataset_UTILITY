import os
import shutil
import argparse
from pathlib import Path

def convert_dataset_structure(source_path, backup=False):
    """
    KU_SEG 형태의 데이터셋을 Spine 형태로 변경하는 함수
    
    기존 구조:
    source_path/
    ├── images/
    │   ├── Train/
    │   └── Validation/
    └── labels/
        ├── Train/
        └── Validation/
    
    변경 후 구조:
    source_path/
    ├── train/
    │   ├── images/
    │   └── labels/
    └── valid/
        ├── images/
        └── labels/
    """
    
    source_path = Path(source_path)
    
    print(f"데이터셋 구조 변경 시작: {source_path}")
    
    # 백업 생성
    if backup:
        backup_path = source_path.parent / f"{source_path.name}_backup"
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(source_path, backup_path)
        print(f"백업 생성 완료: {backup_path}")
    else:
        print("백업 생성 건너뜀")
    
    # 기존 구조 확인
    images_dir = source_path / "images"
    labels_dir = source_path / "labels"
    
    if not images_dir.exists() or not labels_dir.exists():
        print("ERROR: images 또는 labels 디렉토리가 존재하지 않습니다.")
        return False
    
    train_images_dir = images_dir / "Train"
    valid_images_dir = images_dir / "Validation"
    train_labels_dir = labels_dir / "Train"
    valid_labels_dir = labels_dir / "Validation"
    
    # 새로운 구조 생성
    new_train_dir = source_path / "train"
    new_valid_dir = source_path / "valid"
    
    # 임시 디렉토리에서 작업 (충돌 방지)
    temp_dir = source_path / "_temp_conversion"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        # 1. 새로운 구조 생성 (임시 디렉토리)
        temp_train = temp_dir / "train"
        temp_valid = temp_dir / "valid"
        
        temp_train.mkdir()
        temp_valid.mkdir()
        
        (temp_train / "images").mkdir()
        (temp_train / "labels").mkdir()
        (temp_valid / "images").mkdir()
        (temp_valid / "labels").mkdir()
        
        print("새로운 디렉토리 구조 생성 완료")
        
        # 2. 파일 이동
        # Train 이미지 이동
        if train_images_dir.exists():
            for file in train_images_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, temp_train / "images" / file.name)
            print(f"Train 이미지 파일 이동 완료: {len(list(train_images_dir.glob('*')))}개")
        
        # Validation 이미지 이동
        if valid_images_dir.exists():
            for file in valid_images_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, temp_valid / "images" / file.name)
            print(f"Validation 이미지 파일 이동 완료: {len(list(valid_images_dir.glob('*')))}개")
        
        # Train 라벨 이동
        if train_labels_dir.exists():
            for file in train_labels_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, temp_train / "labels" / file.name)
            print(f"Train 라벨 파일 이동 완료: {len(list(train_labels_dir.glob('*')))}개")
        
        # Validation 라벨 이동
        if valid_labels_dir.exists():
            for file in valid_labels_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, temp_valid / "labels" / file.name)
            print(f"Validation 라벨 파일 이동 완료: {len(list(valid_labels_dir.glob('*')))}개")
        
        # 3. 기존 구조 제거
        if images_dir.exists():
            shutil.rmtree(images_dir)
        if labels_dir.exists():
            shutil.rmtree(labels_dir)
        
        # Train.txt, Validation.txt 파일도 제거
        train_txt = source_path / "Train.txt"
        valid_txt = source_path / "Validation.txt"
        if train_txt.exists():
            train_txt.unlink()
        if valid_txt.exists():
            valid_txt.unlink()
        
        print("기존 구조 제거 완료")
        
        # 4. 새로운 구조를 원래 위치로 이동
        shutil.move(str(temp_train), str(new_train_dir))
        shutil.move(str(temp_valid), str(new_valid_dir))
        
        print("새로운 구조로 변경 완료")
        
        # 5. data.yaml 파일 수정
        update_data_yaml(source_path)
        
        # 6. 임시 디렉토리 정리
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"ERROR: 변환 중 오류 발생: {e}")
        # 임시 디렉토리 정리
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False

def update_data_yaml(dataset_path):
    """data.yaml 파일을 새로운 구조에 맞게 수정"""
    dataset_path = Path(dataset_path)
    data_yaml_path = dataset_path / "data.yaml"
    
    if not data_yaml_path.exists():
        print("WARNING: data.yaml 파일이 존재하지 않습니다.")
        return False
    
    try:
        # 기존 data.yaml 읽기
        with open(data_yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"기존 data.yaml 내용:\n{content}")
        
        # 새로운 data.yaml 내용 생성 (Spine 형태)
        new_content = """train: train/images
val: valid/images

nc: 1
names: ['vertebrae']
"""
        
        # data.yaml 파일 업데이트
        with open(data_yaml_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("data.yaml 파일 업데이트 완료")
        print(f"새로운 data.yaml 내용:\n{new_content}")
        return True
        
    except Exception as e:
        print(f"ERROR: data.yaml 업데이트 중 오류 발생: {e}")
        return False

def verify_conversion(dataset_path):
    """변환 결과 검증"""
    dataset_path = Path(dataset_path)
    
    print(f"\n=== 변환 결과 검증: {dataset_path} ===")
    
    train_dir = dataset_path / "train"
    valid_dir = dataset_path / "valid"
    
    if not train_dir.exists():
        print("ERROR: train 디렉토리가 존재하지 않습니다.")
        return False
    
    if not valid_dir.exists():
        print("ERROR: valid 디렉토리가 존재하지 않습니다.")
        return False
    
    # 파일 수 확인
    train_images = len(list((train_dir / "images").glob("*"))) if (train_dir / "images").exists() else 0
    train_labels = len(list((train_dir / "labels").glob("*"))) if (train_dir / "labels").exists() else 0
    valid_images = len(list((valid_dir / "images").glob("*"))) if (valid_dir / "images").exists() else 0
    valid_labels = len(list((valid_dir / "labels").glob("*"))) if (valid_dir / "labels").exists() else 0
    
    print(f"Train - Images: {train_images}, Labels: {train_labels}")
    print(f"Valid - Images: {valid_images}, Labels: {valid_labels}")
    
    # 구조 확인
    expected_structure = [
        "train/images",
        "train/labels", 
        "valid/images",
        "valid/labels"
    ]
    
    all_exist = True
    for path in expected_structure:
        full_path = dataset_path / path
        if full_path.exists():
            print(f"✓ {path}")
        else:
            print(f"✗ {path} (없음)")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="데이터셋 구조를 KU_SEG 형태에서 Spine 형태로 변환")
    parser.add_argument("dataset_path", help="변환할 데이터셋 경로")
    parser.add_argument("--backup", action="store_true", help="변환 전 백업 생성 (기본값: 백업 안함)")
    parser.add_argument("--verify", action="store_true", default=True, help="변환 후 결과 검증 (기본값: 검증함)")
    
    args = parser.parse_args()
    
    print("=== 데이터셋 구조 변환 시작 ===")
    print(f"데이터셋 경로: {args.dataset_path}")
    print(f"백업 생성: {'예' if args.backup else '아니오'}")
    print(f"결과 검증: {'예' if args.verify else '아니오'}")
    print()
    
    if convert_dataset_structure(args.dataset_path, backup=args.backup):
        print("\n변환 성공!")
        if args.verify:
            verify_conversion(args.dataset_path)
    else:
        print("\n변환 실패!")