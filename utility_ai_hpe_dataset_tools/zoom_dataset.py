import cv2
import os
import imutils
import shutil

import utils
import const


def zoom_dataset(images, size = None, ratio = None):
    """
    zoom dataset

    :param images: 이미지 경로
    :param size: 픽셀사이즈 로 리사이징 (h,w)
    :param ratio: 비율로 리사이징 (h,w)
    """
    input_image = cv2.imread(images)
    height, width = input_image.shape[:2]

    if size is not None:
        zoom_width = int(size[0])
        zoom_height = int(size[1])
        
        if height == zoom_height and width == zoom_width:
            output_image = input_image
        else:
            output_image = imutils.resize(input_image, width=zoom_width, height=zoom_height)
    elif ratio is not None:
        x_ratio = float(ratio[0])
        y_ratio = float(ratio[1])
        
        output_image = cv2.resize(input_image, dsize=(0, 0), fx=x_ratio, fy=y_ratio, interpolation=cv2.INTER_AREA)
    else:
        raise Exception(f"size, ratio중 최소 하나는 있어야함")
    
    return output_image

def main(input_dataset, output_dataset='', size = None, ratio = None):
    _SUFFIX = "zoom"
    TEXT_EXT = ".txt"
    
    folder_list = [const.VALID_FOLDER_NAME, const.TRAIN_FOLDER_NAME]
    
    if output_dataset == '':
        output_dataset = f'{input_dataset}_zoom'
    
    if const.TEST_FOLDER_NAME in os.listdir(input_dataset):
        folder_list = [const.TEST_FOLDER_NAME, const.VALID_FOLDER_NAME, const.TRAIN_FOLDER_NAME]
    
    for i in folder_list:
        #makedir
        __input_images_folder = os.path.join(input_dataset,i,const.IMAGES_FOLDER_NAME)
        __input_labels_folder = os.path.join(input_dataset,i,const.LABELS_FOLDER_NAME)
        
        __output_images_folder = os.path.join(output_dataset,i,const.IMAGES_FOLDER_NAME)
        __output_labels_folder = os.path.join(output_dataset,i,const.LABELS_FOLDER_NAME)
        
        utils.directory_check(__output_images_folder)
        utils.directory_check(__output_labels_folder)
        
        for j in os.listdir(__input_images_folder):
            __file_name,image_ext = os.path.splitext(j)
            
            __input_image_path = os.path.join(__input_images_folder, f'{__file_name}{image_ext}')
            __input_label_path = os.path.join(__input_labels_folder, f'{__file_name}{TEXT_EXT}')
            
            __output_image_path = os.path.join(__output_images_folder, f'{__file_name}_{_SUFFIX}{image_ext}')
            __output_label_path = os.path.join(__output_labels_folder, f'{__file_name}_{_SUFFIX}{TEXT_EXT}')
            
            img_data = zoom_dataset(__input_image_path, size, ratio)
            
            utils.save_images(__output_image_path, img_data)
            shutil.copyfile(__input_label_path, __output_label_path)
            
    utils.copy_yaml(input_dataset, output_dataset)
    

def valitate_parser(args):
    if args.size == None and args.ratio == None:
        raise Exception("size, ratio 중 하나는 값이 있어야합니다")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help="입력 데이터셋 폴더")
    parser.add_argument('--output', type=str, required=False, default="", help="결과 데이터셋 폴더")
    parser.add_argument('--size', type=int, required=False, default=None, nargs=2, help="고정사이즈로 리사이징")
    parser.add_argument('--ratio', type=float, required=False, default=None, nargs=2, help="비율로 리사이징")
    
    args = parser.parse_args()
    
    #데이터 검증
    valitate_parser(args)
    print(args)
    main(args.input, args.output, args.size, args.ratio)