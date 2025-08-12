import const
import os
import utils
import cv2
import numpy as np
import shutil

def hsv_image(input_image, hue:float=1.0, saturation:float=1.0, value:float=1.0):
    """
    이미지 hsv 조절
    
    h,s,v 는 0~2 범위

    :param input_image: 입력 이미지
    :param hue: 색조 
    :param saturation: 채도 
    :param value: 명도 
    :return: 결과 이미지
    """
    input_image_np = cv2.imread(input_image)
    
    hsvImage = cv2.cvtColor(input_image_np , cv2.COLOR_BGR2HSV)
    hsvImage = np.float32(hsvImage)

    h, s, v = cv2.split(hsvImage)
    
    if 0 <= hue <= 2 :
        h = np.clip(h * hue, 0, 180)
        
    if 0 <= saturation <= 2 :
        s = np.clip(s * saturation, 0, 255)
        
    if 0 <= value <= 2:
        v = np.clip(v * value, 0, 255)
    
    hsvImage = cv2.merge([h,s,v])
    hsvImage = np.uint8(hsvImage)
    
    result = cv2.cvtColor(hsvImage, cv2.COLOR_HSV2BGR)

    return result

def main(input_dataset, hue, saturation, value, output_dataset=''):
    _SUFFIX = f"hsv_{hue}_{saturation}_{value}"
    TEXT_EXT = ".txt"
    
    folder_list = [const.VALID_FOLDER_NAME, const.TRAIN_FOLDER_NAME]
    
    if output_dataset == '':
        output_dataset = f'{input_dataset}_hsv'
    
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
            
            img_data = hsv_image(__input_image_path, hue=hue, saturation=saturation, value=value)
            
            utils.save_images(__output_image_path, img_data)
            shutil.copyfile(__input_label_path, __output_label_path)

            
    utils.copy_yaml(input_dataset, output_dataset)
    
def valitate_parser(args):
    if 0 <= args.hue <= 2 :
        pass
    else:
        raise
    
    if 0 <= args.saturation <= 2 :
        pass
    else:
        raise
    
    if 0 <= args.value <= 2:
        pass
    else:
        raise
        
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help="입력 데이터셋 폴더")
    parser.add_argument('--output', type=str, required=False, default="", help="결과 데이터셋 폴더")
    parser.add_argument('-H', '--hue', type=float, required=False, default=1.0, help="색조")
    parser.add_argument('-S', '--saturation', type=float, required=False, default=1.0, help="채도")
    parser.add_argument('-V', '--value', type=float, required=False, default=1.0, help="명도")
    
    args = parser.parse_args()
    
    #데이터 검증
    valitate_parser(args)
    print(args)
    main(args.input, args.hue, args.saturation, args.value, args.output)