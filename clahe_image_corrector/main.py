#!/usr/bin/env python3
"""
CLAHE Image Corrector - 메인 실행 스크립트
이미지의 대비와 명도를 개선하는 CLAHE 보정 도구
"""

import argparse
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.corrector import CLAHECorrector

def main():
    parser = argparse.ArgumentParser(
        description="CLAHE(Contrast Limited Adaptive Histogram Equalization) 이미지 보정 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py image.jpg                    # 단일 이미지 보정
  python main.py image.jpg -o output.jpg      # 출력 파일명 지정
  python main.py input_dir/ -d                # 디렉토리 전체 보정
  python main.py image.jpg -c 2.0 -t 16 16    # 파라미터 조정
        """
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="입력 이미지 파일 또는 디렉토리 경로"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="출력 파일/디렉토리 경로 (기본값: 자동 생성)"
    )
    
    parser.add_argument(
        "-d", "--directory",
        action="store_true",
        help="디렉토리 모드 (입력 경로의 모든 이미지 처리)"
    )
    
    parser.add_argument(
        "-c", "--clip-limit",
        type=float,
        default=3.0,
        help="대비 제한 임계값 (기본값: 3.0)"
    )
    
    parser.add_argument(
        "-t", "--tile-size",
        nargs=2,
        type=int,
        default=[8, 8],
        metavar=("WIDTH", "HEIGHT"),
        help="타일 격자 크기 (기본값: 8 8)"
    )
    
    parser.add_argument(
        "-e", "--extensions",
        nargs="+",
        default=[".jpg", ".jpeg", ".png", ".bmp", ".tiff"],
        help="처리할 이미지 확장자 (디렉토리 모드에서만 사용)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="상세 출력 모드"
    )
    
    args = parser.parse_args()
    
    # 입력 경로 확인
    if not os.path.exists(args.input):
        print(f"오류: 입력 경로 '{args.input}'가 존재하지 않습니다.")
        return 1
    
    # CLAHE 보정기 생성
    corrector = CLAHECorrector(
        clip_limit=args.clip_limit,
        tile_grid_size=tuple(args.tile_size)
    )
    
    if args.verbose:
        print(f"CLAHE 파라미터: clip_limit={args.clip_limit}, tile_size={tuple(args.tile_size)}")
    
    try:
        if args.directory or os.path.isdir(args.input):
            # 디렉토리 모드
            if args.verbose:
                print(f"디렉토리 모드: {args.input}")
            
            processed_count = corrector.process_directory(
                input_dir=args.input,
                output_dir=args.output,
                extensions=tuple(args.extensions)
            )
            
            if processed_count > 0:
                print(f"성공: {processed_count}개의 이미지가 보정되었습니다.")
                return 0
            else:
                print("오류: 처리된 이미지가 없습니다.")
                return 1
        else:
            # 단일 파일 모드
            if args.verbose:
                print(f"단일 파일 모드: {args.input}")
            
            success = corrector.process_single_image(
                input_path=args.input,
                output_path=args.output
            )
            
            if success:
                print("이미지 보정이 완료되었습니다.")
                return 0
            else:
                print("오류: 이미지 보정에 실패했습니다.")
                return 1
                
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"예상치 못한 오류: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)