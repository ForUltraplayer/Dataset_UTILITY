import cv2
import imutils
import pandas as pd
import numpy as np
import utils
import const
import os

from math import cos, sin, radians


def cut_empty_area(input_image):
    """
    4채널 오브젝트 이미지에서 유효한 영역만 잘라냄
    :param input_image: 입력 이미지 (경로 또는 ndarray)
    :return: 결과이미지 및 유효영역좌표(원본과 동일하면 None)
    """
    input_image_np = input_image

    # 3채널 이하 이미지 걸러내기
    if input_image_np.shape[2] <= 3:
        return input_image_np, None

    # 배경 날림이 이미 이루어진 오브젝트 이미지인 경우
    imcanny = cv2.Canny(input_image_np, 1, 10)
    x, y, w, h = cv2.boundingRect(imcanny)

    # imcanny = cv2.Canny(input_image_np, 50, 150)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    # closed = cv2.morphologyEx(imcanny, cv2.MORPH_CLOSE, kernel)
    # contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #
    # x, y, w, h = input_image_np.shape[1], input_image_np.shape[1], 0, 0
    # for contour in contours:
    #     x_, y_, w_, h_ = cv2.boundingRect(contour)
    #     x = x_ if x_ < x else x
    #     y = y_ if y_ < y else y
    #     w = w_ if w_ > w else w
    #     h = h_ if h_ > h else h

    output_image = input_image_np[y:y+h, x:x+w].copy()
    
    return output_image, (x, y, w, h) if (x, y, w, h) != (0, 0, input_image_np.shape[1], input_image_np.shape[0]) else None

def rotate_bbox_coord(angle, origin_coord=None, before_size=None, after_size=None):
    """
    pixel 좌표 기준으로 회전 후의 좌표를 구한다.
    :param angle: 회전각 (반시계방향)
    :param origin_coord: 회전 전의 좌표들 [(x1, y1, x2, y2), ...]
    :param before_size: 회전 전의 이미지 크기 (height, width)
    :param after_size; 회전 후의 이미지 크기 (height, width)
    """

    # 회전하기 전 이미지 크기 및 center좌표
    before_h, before_w = before_size
    cx, cy = round(before_w / 2.0), round(before_h / 2.0)

    # 회전한 후의 이미지 크기 및 center좌표
    after_h, after_w = after_size
    acx = cx + round((after_w - before_w) / 2.0)
    acy = cy + round((after_h - before_h) / 2.0)

    rad = radians(360 - angle)

    rotated_coord = []
    rx = []
    ry = []

    for row in origin_coord:
        current_row = []
        
        #class
        current_row.append(row[0])

        #bbox
        x1, y1, x2, y2 = row[1:5]

        rx.append(round((x1 - cx) * cos(rad) - (y1 - cy) * sin(rad) + acx))
        ry.append(round((x1 - cx) * sin(rad) + (y1 - cy) * cos(rad) + acy))

        rx.append(round((x2 - cx) * cos(rad) - (y2 - cy) * sin(rad) + acx))
        ry.append(round((x2 - cx) * sin(rad) + (y2 - cy) * cos(rad) + acy))

        rx.append(round((x1 - cx) * cos(rad) - (y2 - cy) * sin(rad) + acx))
        ry.append(round((x1 - cx) * sin(rad) + (y2 - cy) * cos(rad) + acy))

        rx.append(round((x2 - cx) * cos(rad) - (y1 - cy) * sin(rad) + acx))
        ry.append(round((x2 - cx) * sin(rad) + (y1 - cy) * cos(rad) + acy))

        current_row += [min(rx), min(ry), max(rx), max(ry)]
        rx.clear()
        ry.clear()
        
        #keypoint
        keypoints = row[5:]
        
        reshaped_keypoints = keypoints.reshape(-1, 3)
        split_keypoints = np.vsplit(reshaped_keypoints, reshaped_keypoints.shape[0])
        
        for kpt_group in split_keypoints:
            kpt_x, kpt_y, v = kpt_group.flatten()
            kpt_x_rot = (kpt_x - cx) * cos(rad) - (kpt_y - cy) * sin(rad) + acx
            kpt_y_rot = (kpt_x - cx) * sin(rad) + (kpt_y - cy) * cos(rad) + acy
            v = int(float(v))
            
            if kpt_x_rot < 0 or kpt_x_rot > after_w or kpt_y_rot < 0 or kpt_y_rot > after_h:
                # invisible
                v = 0 
                     
            current_row += [kpt_x_rot, kpt_y_rot, v]
        rotated_coord.append(current_row)

    return np.array(rotated_coord, dtype=np.float64)

def rotate_dataset(images, labels, angle, bound):
    """_summary_

    :param images: _description_
    :param labels: _description_
    :param angle: 회전각도 (반시계 방향)
    :param bound: 이미지 회전시 경계 잘림 처리 유무
    :return: _description_
    """
    input_image = cv2.imread(images)
    
    before_h, before_w = input_image.shape[:2]
    
    # image rotate
    if angle % 360 == 0:
        # 0도인 경우 의미없으므로 그대로 return
        rotated_image = input_image
    else:
        if bound:
            rotated_image = imutils.rotate_bound(input_image, -angle)
        else:
            rotated_image = imutils.rotate(input_image, angle)
            
    cut_image, cut_coord = cut_empty_area(rotated_image)
    after_h, after_w = rotated_image.shape[:2]
    
    try:
        rotated_label_yolo = pd.DataFrame().to_numpy()
        input_label = pd.read_csv(labels, sep=' ', header=None).to_numpy() # cls cx cy w h kpt_x1 kpt_y1 kpt_v1
        input_label_coco = utils.yolo_to_coco(input_image, input_label)
        
        rotated_pixel = rotate_bbox_coord(angle, input_label_coco, (before_h, before_w), (after_h, after_w))

        #bounding box가 범위를 넘어가는지 재계산
        x, y, w, h = cut_coord if cut_coord is not None else (0, 0, before_w, before_h)
        for idx, coord in enumerate(rotated_pixel):
            bx1, by1, bx2, by2 = coord[1:5]

            coord[1] = min(w, max(0, (bx1-x)))
            coord[2] = min(h, max(0, (by1-y)))
            coord[3] = min(w, max(0, (bx2-x)))
            coord[4] = min(h, max(0, (by2-y)))
        
        rotated_label_yolo = utils.coco_to_yolo(rotated_image, rotated_pixel)
                

    except pd.errors.EmptyDataError:
        pass
            
    finally:
        return rotated_image, rotated_label_yolo
    
def main(input_dataset, angle, bound, output_dataset=''):
    _SUFFIX = f"rot_{angle}"
    TEXT_EXT = ".txt"
    
    folder_list = [const.VALID_FOLDER_NAME, const.TRAIN_FOLDER_NAME]
    
    if output_dataset == '':
        output_dataset = f'{input_dataset}_rot{angle}'
    
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
            
            img_data, label_data = rotate_dataset(__input_image_path, __input_label_path, angle, bound)
            
            utils.save_images(__output_image_path, img_data)
            utils.save_labels(__output_label_path, label_data)
            
    utils.copy_yaml(input_dataset, output_dataset)
    
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help="입력 데이터셋 폴더")
    parser.add_argument('--angle', type=int, required=True, help="회전각도")
    parser.add_argument('--bound', action='store_true', help="이미지 회전시 이미지 잘림 여부 (옵션을 줄시 안 잘림)")
    parser.add_argument('--output', type=str, required=False, default="", help="결과 데이터셋 폴더")
    
    args = parser.parse_args()
    
    main(args.input, args.angle, args.bound, args.output)
    
    # NOTE(JWKIM): bounding box 좌표 보정이 필요함