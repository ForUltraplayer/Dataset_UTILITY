import cv2
import pandas as pd
import os

import utils
import const

def flip_dataset(images, labels, image_flip=1):
    """
    flip dataset

    :param images: 이미지 경로
    :param labels: 라벨 경로
    :param flip: 0: 상하 반전, 1: 좌우 반전
    """
    # image flip
    input_image = cv2.imread(images)
    output_image = cv2.flip(input_image, image_flip) 
    
    try:
        # label flip # xywh xyv xyv ...
        input_label = pd.read_csv(labels, sep=' ', header=None).to_numpy()
        for idx, row in enumerate(input_label):
            
            if image_flip == 1:
                # 좌우반전 -> x값만 변경
                __BBOX_X = 1
                __KPT_X = __BBOX_X + 4
                __kpt_len = int(len(row[5:])/3)
                
                #bbox
                row[__BBOX_X] = 1.0 - row[__BBOX_X]
                
                #kpt
                for i in range(__kpt_len):
                    row[__KPT_X + (3*i)] = 1.0 - row[__KPT_X + (3*i)]
                    
                for j in range(len(row)):
                    if j == 0:
                        row[j] = int(row[j])
                    else:
                        row[j] = round(row[j],4)
                        
            else:
                # 상하반전
                __BBOX_Y = 2
                __KPT_Y = __BBOX_Y + 4
                __kpt_len = int(len(row[5:])/3)
                
                row[__BBOX_Y] = 1.0 - row[__BBOX_Y]
                
                for i in range(__kpt_len):
                    row[__KPT_Y + (3*i)] = 1.0 - row[__KPT_Y + (3*i)]
                    
                for j in range(len(row)):
                    if j == 0:
                        row[j] = int(row[j])
                    else:
                        row[j] = round(row[j],4)
    
    except pd.errors.EmptyDataError:
        input_label = pd.DataFrame().to_numpy()
        
    finally:
        return output_image, input_label

def main(input_dataset, output_dataset=''):
    _SUFFIX = "flip"
    TEXT_EXT = ".txt"
    
    folder_list = [const.VALID_FOLDER_NAME, const.TRAIN_FOLDER_NAME]
    
    if output_dataset == '':
        output_dataset = f'{input_dataset}_flip'
    
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
            
            img_data, label_data = flip_dataset(__input_image_path, __input_label_path)
            
            utils.save_images(__output_image_path, img_data)
            utils.save_labels(__output_label_path, label_data)
            
    utils.copy_yaml(input_dataset, output_dataset)
            
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help="입력 데이터셋 폴더")
    parser.add_argument('--output', type=str, required=False, default="", help="결과 데이터셋 폴더")
    
    args = parser.parse_args()
    
    main(args.input, args.output)