import cv2
import numpy as np
import os
from pathlib import Path
from typing import Tuple, Optional

class CLAHECorrector:
    """
    CLAHE(Contrast Limited Adaptive Histogram Equalization) 이미지 보정기
    """
    
    def __init__(self, clip_limit: float = 3.0, tile_grid_size: Tuple[int, int] = (8, 8)):
        """
        CLAHE 보정기 초기화
        
        Args:
            clip_limit: 대비 제한 임계값 (기본값: 3.0)
            tile_grid_size: 타일 격자 크기 (기본값: (8, 8))
        """
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    
    def correct_image(self, image: np.ndarray) -> np.ndarray:
        """
        이미지에 CLAHE 보정 적용
        
        Args:
            image: 입력 이미지 (BGR 포맷)
            
        Returns:
            보정된 이미지
        """
        if image is None:
            raise ValueError("입력 이미지가 None입니다.")
        
        # BGR을 LAB 색공간으로 변환
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # L(명도) 채널에 CLAHE 적용
        cl = self.clahe.apply(l)
        
        # 보정된 L 채널과 기존 a, b 채널 합성
        corrected_lab = cv2.merge((cl, a, b))
        
        # LAB을 다시 BGR로 변환
        corrected_image = cv2.cvtColor(corrected_lab, cv2.COLOR_LAB2BGR)
        
        return corrected_image
    
    def process_single_image(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """
        단일 이미지 처리
        
        Args:
            input_path: 입력 이미지 경로
            output_path: 출력 이미지 경로 (None시 자동 생성)
            
        Returns:
            처리 성공 여부
        """
        try:
            # 이미지 읽기
            image = cv2.imread(input_path)
            if image is None:
                print(f"오류: {input_path}에서 이미지를 읽을 수 없습니다.")
                return False
            
            # 보정 적용
            corrected_image = self.correct_image(image)
            
            # 출력 경로 설정
            if output_path is None:
                input_path_obj = Path(input_path)
                output_path = str(input_path_obj.parent / f"{input_path_obj.stem}_clahe{input_path_obj.suffix}")
            
            # 출력 디렉토리 생성
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            # 이미지 저장
            success = cv2.imwrite(output_path, corrected_image)
            if success:
                print(f"보정된 이미지 저장: {output_path}")
                return True
            else:
                print(f"오류: {output_path}에 이미지를 저장할 수 없습니다.")
                return False
                
        except Exception as e:
            print(f"처리 중 오류 발생: {str(e)}")
            return False
    
    def process_directory(self, input_dir: str, output_dir: Optional[str] = None, 
                         extensions: Tuple[str, ...] = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')) -> int:
        """
        디렉토리 내 모든 이미지를 재귀적으로 처리하며 디렉토리 구조 유지
        
        Args:
            input_dir: 입력 디렉토리 경로
            output_dir: 출력 디렉토리 경로 (None시 자동 생성)
            extensions: 처리할 이미지 확장자
            
        Returns:
            처리된 이미지 수
        """
        input_path = Path(input_dir)
        if not input_path.exists() or not input_path.is_dir():
            print(f"오류: {input_dir}는 유효한 디렉토리가 아닙니다.")
            return 0
        
        # 출력 디렉토리 설정
        if output_dir is None:
            output_path = input_path / "corrected"
        else:
            output_path = Path(output_dir)
        
        # 재귀적으로 모든 이미지 파일 찾기
        image_files = []
        for ext in extensions:
            image_files.extend(input_path.rglob(f"*{ext}"))
            image_files.extend(input_path.rglob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"오류: {input_dir}에서 지원되는 이미지 파일을 찾을 수 없습니다.")
            return 0
        
        # 각 이미지 처리
        processed_count = 0
        for img_file in image_files:
            # 상대 경로 계산하여 디렉토리 구조 유지
            relative_path = img_file.relative_to(input_path)
            output_file = output_path / relative_path.parent / f"{relative_path.stem}_clahe{relative_path.suffix}"
            
            # 출력 디렉토리 생성
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if self.process_single_image(str(img_file), str(output_file)):
                processed_count += 1
        
        print(f"총 {processed_count}개의 이미지가 처리되었습니다.")
        return processed_count
    
    def update_parameters(self, clip_limit: float, tile_grid_size: Tuple[int, int]):
        """
        CLAHE 파라미터 업데이트
        
        Args:
            clip_limit: 새로운 대비 제한 임계값
            tile_grid_size: 새로운 타일 격자 크기
        """
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)