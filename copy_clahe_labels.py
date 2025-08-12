import os
import shutil
from pathlib import Path

def copy_labels_for_clahe_images():
    """
    _clahe 이미지들에 대응하는 라벨 파일을 복사하는 함수
    """
    base_path = Path(__file__).parent
    
    # Train과 Validation 폴더 처리
    for folder in ['Train', 'Validation']:
        images_path = base_path / 'images' / folder
        labels_path = base_path / 'labels' / folder
        
        # _clahe 이미지 파일들 찾기
        clahe_images = list(images_path.glob('*_clahe.jpg'))
        
        print(f"\n{folder} 폴더에서 {len(clahe_images)}개의 _clahe 이미지 발견")
        
        copied_count = 0
        
        for clahe_image in clahe_images:
            # 원본 이미지 파일명 추출 (_clahe.jpg 제거)
            original_name = clahe_image.name.replace('_clahe.jpg', '.jpg')
            
            # 대응하는 원본 라벨 파일 경로
            original_label = labels_path / original_name.replace('.jpg', '.txt')
            
            # _clahe 라벨 파일 경로
            clahe_label = labels_path / clahe_image.name.replace('.jpg', '.txt')
            
            # 원본 라벨 파일이 존재하고, _clahe 라벨 파일이 없는 경우에만 복사
            if original_label.exists() and not clahe_label.exists():
                try:
                    shutil.copy2(original_label, clahe_label)
                    copied_count += 1
                    print(f"복사됨: {original_label.name} -> {clahe_label.name}")
                except Exception as e:
                    print(f"복사 실패 {original_label.name}: {e}")
            elif not original_label.exists():
                print(f"원본 라벨 파일 없음: {original_label.name}")
            else:
                print(f"이미 존재함: {clahe_label.name}")
        
        print(f"{folder} 폴더에서 총 {copied_count}개의 라벨 파일 복사 완료")

if __name__ == "__main__":
    copy_labels_for_clahe_images()
    print("\n모든 _clahe 이미지에 대한 라벨 파일 복사 작업 완료!")