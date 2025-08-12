import os
import shutil
import argparse
from pathlib import Path

def revert_dataset_structure(source_path, backup=False):
    """
    Spine 형태의 데이터셋을 KU_SEG 형태로 변경하는 함수
    
    기존 구조 (Spine):
    source_path/
    ├── train/
    │   ├── images/
    │   └── labels/
    └── valid/
        ├── images/
        └── labels/
    
    변경 후 구조 (KU_SEG):
    source_path/
    ├── images/
    │   ├── Train/
    │   └── Validation/
    └── labels/
        ├── Train/
        └── Validation/
    """
    
    source_path = Path(source_path)
    
    print(f"데이터셋 구조 역변환 시작: {source_path}")
    
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
    train_dir = source_path / "train"
    valid_dir = source_path / "valid"
    
    if not train_dir.exists() or not valid_dir.exists():
        print("ERROR: train 또는 valid 디렉토리가 존재하지 않습니다.")
        return False
    
    train_images_dir = train_dir / "images"
    train_labels_dir = train_dir / "labels"
    valid_images_dir = valid_dir / "images"
    valid_labels_dir = valid_dir / "labels"
    
    # 새로운 구조 생성을 위한 디렉토리
    new_images_dir = source_path / "images"
    new_labels_dir = source_path / "labels"
    
    # 임시 디렉토리에서 작업 (충돌 방지)
    temp_dir = source_path / "_temp_reversion"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        # 1. 새로운 구조 생성 (임시 디렉토리)
        temp_images = temp_dir / "images"
        temp_labels = temp_dir / "labels"
        
        temp_images.mkdir()
        temp_labels.mkdir()
        
        (temp_images / "Train").mkdir()
        (temp_images / "Validation").mkdir()
        (temp_labels / "Train").mkdir()
        (temp_labels / "Validation").mkdir()
        
        print("새로운 디렉토리 구조 생성 완료")
        
        # 2. 파일 이동
        # Train 이미지 이동
        if train_images_dir.exists():
            for file in train_images_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, temp_images / "Train" / file.name)
            print(f"Train 이미지 파일 이동 완료: {len(list(train_images_dir.glob('*')))}개")
        
        # Valid 이미지를 Validation으로 이동
        if valid_images_dir.exists():
            for file in valid_images_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, temp_images / "Validation" / file.name)
            print(f"Valid 이미지 파일 이동 완료: {len(list(valid_images_dir.glob('*')))}개")
        
        # Train 라벨 이동
        if train_labels_dir.exists():
            for file in train_labels_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, temp_labels / "Train" / file.name)
            print(f"Train 라벨 파일 이동 완료: {len(list(train_labels_dir.glob('*')))}개")
        
        # Valid 라벨을 Validation으로 이동
        if valid_labels_dir.exists():
            for file in valid_labels_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, temp_labels / "Validation" / file.name)
            print(f"Valid 라벨 파일 이동 완료: {len(list(valid_labels_dir.glob('*')))}개")
        
        # 3. 기존 구조 제거
        if train_dir.exists():
            shutil.rmtree(train_dir)
        if valid_dir.exists():
            shutil.rmtree(valid_dir)
        
        print("기존 구조 제거 완료")
        
        # 4. 새로운 구조를 원래 위치로 이동
        shutil.move(str(temp_images), str(new_images_dir))
        shutil.move(str(temp_labels), str(new_labels_dir))
        
        print("새로운 구조로 변경 완료")
        
        # 5. data.yaml 파일 수정
        update_data_yaml(source_path)
        
        # 6. Train.txt, Validation.txt 파일 생성
        create_txt_files(source_path)
        
        # 7. 임시 디렉토리 정리
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"ERROR: 역변환 중 오류 발생: {e}")
        # 임시 디렉토리 정리
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False

def update_data_yaml(dataset_path):
    """data.yaml 파일을 KU_SEG 구조에 맞게 수정"""
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
        
        # 새로운 data.yaml 내용 생성 (KU_SEG 형태)
        new_content = """train: images/Train
val: images/Validation

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

def create_txt_files(dataset_path):
    """Train.txt, Validation.txt 파일 생성"""
    dataset_path = Path(dataset_path)
    
    try:
        # Train.txt 생성
        train_images_dir = dataset_path / "images" / "Train"
        if train_images_dir.exists():
            train_files = [f.name for f in train_images_dir.glob("*") if f.is_file()]
            train_txt_path = dataset_path / "Train.txt"
            
            with open(train_txt_path, 'w', encoding='utf-8') as f:
                for file_name in sorted(train_files):
                    f.write(f"{file_name}\n")
            
            print(f"Train.txt 파일 생성 완료: {len(train_files)}개 파일")
        
        # Validation.txt 생성
        valid_images_dir = dataset_path / "images" / "Validation"
        if valid_images_dir.exists():
            valid_files = [f.name for f in valid_images_dir.glob("*") if f.is_file()]
            valid_txt_path = dataset_path / "Validation.txt"
            
            with open(valid_txt_path, 'w', encoding='utf-8') as f:
                for file_name in sorted(valid_files):
                    f.write(f"{file_name}\n")
            
            print(f"Validation.txt 파일 생성 완료: {len(valid_files)}개 파일")
        
        return True
        
    except Exception as e:
        print(f"ERROR: txt 파일 생성 중 오류 발생: {e}")
        return False

def verify_reversion(dataset_path):
    """역변환 결과 검증"""
    dataset_path = Path(dataset_path)
    
    print(f"\n=== 역변환 결과 검증: {dataset_path} ===")
    
    images_dir = dataset_path / "images"
    labels_dir = dataset_path / "labels"
    
    if not images_dir.exists():
        print("ERROR: images 디렉토리가 존재하지 않습니다.")
        return False
    
    if not labels_dir.exists():
        print("ERROR: labels 디렉토리가 존재하지 않습니다.")
        return False
    
    # 파일 수 확인
    train_images = len(list((images_dir / "Train").glob("*"))) if (images_dir / "Train").exists() else 0
    train_labels = len(list((labels_dir / "Train").glob("*"))) if (labels_dir / "Train").exists() else 0
    valid_images = len(list((images_dir / "Validation").glob("*"))) if (images_dir / "Validation").exists() else 0
    valid_labels = len(list((labels_dir / "Validation").glob("*"))) if (labels_dir / "Validation").exists() else 0
    
    print(f"Train - Images: {train_images}, Labels: {train_labels}")
    print(f"Validation - Images: {valid_images}, Labels: {valid_labels}")
    
    # 구조 확인
    expected_structure = [
        "images/Train",
        "images/Validation", 
        "labels/Train",
        "labels/Validation"
    ]
    
    all_exist = True
    for path in expected_structure:
        full_path = dataset_path / path
        if full_path.exists():
            print(f"✓ {path}")
        else:
            print(f"✗ {path} (없음)")
            all_exist = False
    
    # txt 파일 확인
    train_txt = dataset_path / "Train.txt"
    valid_txt = dataset_path / "Validation.txt"
    
    if train_txt.exists():
        print(f"✓ Train.txt")
    else:
        print(f"✗ Train.txt (없음)")
        all_exist = False
        
    if valid_txt.exists():
        print(f"✓ Validation.txt")
    else:
        print(f"✗ Validation.txt (없음)")
        all_exist = False
    
    return all_exist

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="데이터셋 구조를 Spine 형태에서 KU_SEG 형태로 역변환")
    parser.add_argument("dataset_path", help="역변환할 데이터셋 경로")
    parser.add_argument("--backup", action="store_true", help="변환 전 백업 생성 (기본값: 백업 안함)")
    parser.add_argument("--verify", action="store_true", default=True, help="변환 후 결과 검증 (기본값: 검증함)")
    
    args = parser.parse_args()
    
    print("=== 데이터셋 구조 역변환 시작 ===")
    print(f"데이터셋 경로: {args.dataset_path}")
    print(f"백업 생성: {'예' if args.backup else '아니오'}")
    print(f"결과 검증: {'예' if args.verify else '아니오'}")
    print()
    
    if revert_dataset_structure(args.dataset_path, backup=args.backup):
        print("\n역변환 성공!")
        if args.verify:
            verify_reversion(args.dataset_path)
    else:
        print("\n역변환 실패!")