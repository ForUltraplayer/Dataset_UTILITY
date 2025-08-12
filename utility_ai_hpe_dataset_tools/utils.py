import os
import glob
import yaml
import cv2
import pandas as pd
import numpy as np
import shutil

def get_kpt_shape(input):
    """
    인풋 폴더에서 yaml(yml) 파일 찾아서 keypoint 갯수 확인

    :return: _description_
    """
    input_path = os.path.realpath(input)
    print(input_path)
    
    yaml_path = f"{input_path}{os.path.sep}*.yaml"
    yaml_path_list = glob.glob(yaml_path)
    
    if not yaml_path_list:
        yaml_path = f"{input_path}{os.path.sep}*.yml"
        yaml_path_list = glob.glob(yaml_path)
        
        if not yaml_path_list:
            raise FileNotFoundError("not found yaml(yml) files")
    
    with open(yaml_path_list[0]) as f:
        yaml_data = yaml.safe_load(f)
    
    return len(yaml_data.get("flip_idx"))

def directory_check(output):
    try:
        if not os.path.exists(output):
            os.makedirs(output, exist_ok=True)    
        return True
    
    except Exception as e:
        return False

def generate_fmt(num_keypoints, box_fmt='%.4f', kpt_fmt=('%.4f', '%.4f', '%d')):
    """
    num_keypoints: keypoint 개수
    box_fmt: x,y,w,h 포맷 (기본 %.2f)
    kpt_fmt: (x, y, v) keypoint 포맷
    """
    fmt = ['%d']  # cls
    fmt += [box_fmt] * 4  # x, y, w, h
    fmt += list(kpt_fmt) * num_keypoints  # x1, y1, v1, ...
    return fmt

def save_labels(filename, data_lines):
    """
    각 row의 구조: [cls, x, y, w, h, (x1, y1, v1), (x2, y2, v2), ...]
    data_lines: List of Lists (가변 길이 row들)
    """
    with open(filename, 'w') as f:
        for line in data_lines:
            row_fmt = ['%d'] + ['%.2f'] * 4  # cls, x, y, w, h
            num_kpts = (len(line) - 5) // 3
            row_fmt += (['%.2f', '%.2f', '%d'] * num_kpts)
            str_line = ' '.join(fmt % val for fmt, val in zip(row_fmt, line))
            f.write(str_line + '\n')
            
def save_images(filename, image_datas):
    cv2.imwrite(filename, image_datas)
    
def copy_yaml(input_folder, output_folder):
    """
    input_folder 에 있는 .yaml 혹은 .yml 파일 output_folder로 복사

    :param input_folder: _description_
    :param output_folder: _description_
    """
    input_path = os.path.realpath(input_folder)
    
    yaml_path = f"{input_path}{os.path.sep}*.yaml"
    yaml_path_list = glob.glob(yaml_path)

    yml_path = f"{input_path}{os.path.sep}*.yml"
    yaml_path_list = yaml_path_list + glob.glob(yml_path)
        
    for i in yaml_path_list:
        output_path = os.path.join(output_folder,os.path.basename(i))
        shutil.copy(i, output_path)
        

def yolo_to_coco(img_data, label_data):
    """
    cls cx cy w h kpt_x1 kpt_y1 kpt_v1 ... -> cls x1 y1 x2 y2 kpt_x1 kpt_y1 kpt_v1 ... 
    """
    result = []
    
    height, width = img_data.shape[:2]
    
    for row in label_data:
        current_row = []
        
        #append class no
        _cls = int(float(row[0]))
        current_row += [_cls]
        
        #convert cx cy w h
        cx, cy, w, h = row[1:5]
        w = round(width * w)
        h = round(height * h)
        (x1, y1) = (round((width * cx) - (w / 2)), round((height * cy) - (h / 2)))
        (x2, y2) = (x1 + w, y1 + h)
        current_row += [x1, y1, x2, y2]
        
        #convert keypoint
        keypoints = row[5:]
        
        reshaped_keypoints = keypoints.reshape(-1, 3)
        split_keypoints = np.vsplit(reshaped_keypoints, reshaped_keypoints.shape[0])
        
        for kpt_group in split_keypoints:
            kpt_x, kpt_y, v = kpt_group.flatten()
            kpt_x1 = round(width * kpt_x)
            kpt_y1 = round(height * kpt_y)
            v = int(float(v))
            current_row += [kpt_x1, kpt_y1, v]
        
        result.append(current_row)
    
    return np.array(result, dtype=np.float64)


def coco_to_yolo(img_data, label_data):
    """
    cls x1 y1 x2 y2 kpt_x1 kpt_y1 kpt_v1 ... -> cls cx cy w h kpt_x1 kpt_y1 kpt_v1 ... 
    """
    result = []
    
    height, width = img_data.shape[:2]
    
    for row in label_data:
        current_row = []
        
        #append class no
        _cls = int(float(row[0]))
        current_row += [_cls]
        
        #convert x1 y1 x2 y2 작업중
        x1, y1, x2, y2 = row[1:5]
        cx = (x1 + ((x2-x1) / 2)) / width
        cy = (y1 + ((y2-y1) / 2)) / height
        w = (x2-x1) / width
        h = (y2-y1) / height
        current_row += [cx, cy, w, h]
        
        #convert keypoint
        keypoints = row[5:]
        
        reshaped_keypoints = keypoints.reshape(-1, 3)
        split_keypoints = np.vsplit(reshaped_keypoints, reshaped_keypoints.shape[0])
        
        for kpt_group in split_keypoints:
            kpt_x, kpt_y, v = kpt_group.flatten()
            kpt_x1 = kpt_x / width
            kpt_y1 = kpt_y / height
            v = int(float(v))
            current_row += [kpt_x1, kpt_y1, v]
        
        result.append(current_row)
    
    return np.array(result, dtype=np.float64)
    

if __name__ == "__main__":
    pass