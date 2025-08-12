import cv2
import os
import shutil
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path

def load_image(image_path: str) -> Optional[np.ndarray]:
    """
    Load image from file
    
    Args:
        image_path: Path to image file
        
    Returns:
        Image array or None if failed to load
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Warning: Could not load image: {image_path}")
            return None
        return image
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def save_image(image: np.ndarray, output_path: str) -> bool:
    """
    Save image to file
    
    Args:
        image: Image array to save
        output_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        success = cv2.imwrite(output_path, image)
        if not success:
            print(f"Warning: Failed to save image: {output_path}")
        return success
    except Exception as e:
        print(f"Error saving image {output_path}: {e}")
        return False

def flip_image_horizontal(image: np.ndarray) -> np.ndarray:
    """
    Flip image horizontally
    
    Args:
        image: Input image
        
    Returns:
        Horizontally flipped image
    """
    return cv2.flip(image, 1)

def flip_image_vertical(image: np.ndarray) -> np.ndarray:
    """
    Flip image vertically
    
    Args:
        image: Input image
        
    Returns:
        Vertically flipped image
    """
    return cv2.flip(image, 0)

def rotate_image_bound(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate image with expanded canvas to avoid cropping
    
    Args:
        image: Input image
        angle: Rotation angle in degrees (positive = counter-clockwise)
        
    Returns:
        Rotated image with expanded canvas
    """
    if angle % 360 == 0:
        return image.copy()
    
    height, width = image.shape[:2]
    
    # Calculate rotation center
    center = (width // 2, height // 2)
    
    # Get rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Calculate new bounding dimensions
    cos = abs(rotation_matrix[0, 0])
    sin = abs(rotation_matrix[0, 1])
    new_width = int((height * sin) + (width * cos))
    new_height = int((height * cos) + (width * sin))
    
    # Adjust rotation matrix for translation
    rotation_matrix[0, 2] += (new_width / 2) - center[0]
    rotation_matrix[1, 2] += (new_height / 2) - center[1]
    
    # Apply rotation
    rotated = cv2.warpAffine(image, rotation_matrix, (new_width, new_height), 
                            borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    
    return rotated

def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate image around center (may crop corners)
    
    Args:
        image: Input image
        angle: Rotation angle in degrees (positive = counter-clockwise)
        
    Returns:
        Rotated image (same size as input)
    """
    if angle % 360 == 0:
        return image.copy()
    
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height), 
                            borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    
    return rotated

def get_dataset_structure(dataset_path: str) -> dict:
    """
    Get YOLO dataset structure
    
    Args:
        dataset_path: Path to dataset root
        
    Returns:
        Dictionary with dataset structure info
    """
    structure = {
        'train': {'images': [], 'labels': []},
        'valid': {'images': [], 'labels': []},
        'test': {'images': [], 'labels': []}
    }
    
    for split in ['train', 'valid', 'test']:
        images_dir = os.path.join(dataset_path, split, 'images')
        labels_dir = os.path.join(dataset_path, split, 'labels')
        
        if os.path.exists(images_dir):
            structure[split]['images'] = [
                f for f in os.listdir(images_dir) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
            ]
        
        if os.path.exists(labels_dir):
            structure[split]['labels'] = [
                f for f in os.listdir(labels_dir) 
                if f.lower().endswith('.txt')
            ]
    
    return structure

def create_output_directories(output_path: str, splits: List[str]):
    """
    Create output directory structure
    
    Args:
        output_path: Output dataset root path
        splits: List of dataset splits (e.g., ['train', 'valid', 'test'])
    """
    for split in splits:
        os.makedirs(os.path.join(output_path, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(output_path, split, 'labels'), exist_ok=True)

def copy_yaml_file(input_path: str, output_path: str):
    """
    Copy data.yaml file to output directory
    
    Args:
        input_path: Input dataset path
        output_path: Output dataset path
    """
    yaml_files = ['data.yaml', 'dataset.yaml', 'config.yaml']
    
    for yaml_file in yaml_files:
        src = os.path.join(input_path, yaml_file)
        if os.path.exists(src):
            dst = os.path.join(output_path, yaml_file)
            try:
                shutil.copy2(src, dst)
                print(f"Copied {yaml_file} to output directory")
                break
            except Exception as e:
                print(f"Warning: Failed to copy {yaml_file}: {e}")

def get_corresponding_files(images_dir: str, labels_dir: str) -> List[Tuple[str, str]]:
    """
    Get corresponding image and label file pairs
    
    Args:
        images_dir: Directory containing images
        labels_dir: Directory containing labels
        
    Returns:
        List of (image_path, label_path) tuples
    """
    file_pairs = []
    
    if not os.path.exists(images_dir):
        return file_pairs
    
    for image_file in os.listdir(images_dir):
        if not image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            continue
        
        # Get corresponding label file
        image_name = os.path.splitext(image_file)[0]
        label_file = f"{image_name}.txt"
        
        image_path = os.path.join(images_dir, image_file)
        label_path = os.path.join(labels_dir, label_file)
        
        # Only include if both files exist
        if os.path.exists(label_path):
            file_pairs.append((image_path, label_path))
        else:
            print(f"Warning: No corresponding label file for {image_file}")
    
    return file_pairs