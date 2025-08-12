import numpy as np
from typing import List, Tuple, Optional

def parse_yolo_segmentation_label(label_line: str) -> Tuple[int, np.ndarray]:
    """
    Parse YOLO segmentation label line
    
    Args:
        label_line: Single line from YOLO label file
        
    Returns:
        Tuple of (class_id, polygon_points)
        polygon_points shape: (n_points, 2) where each point is [x, y]
    """
    parts = label_line.strip().split()
    if len(parts) < 7:  # class_id + at least 3 points (6 coordinates)
        raise ValueError(f"Invalid label format: {label_line}")
    
    class_id = int(parts[0])
    coords = [float(x) for x in parts[1:]]
    
    # Ensure even number of coordinates (x,y pairs)
    if len(coords) % 2 != 0:
        raise ValueError(f"Odd number of coordinates: {len(coords)}")
    
    # Reshape to (n_points, 2)
    polygon_points = np.array(coords).reshape(-1, 2)
    
    return class_id, polygon_points

def format_yolo_segmentation_label(class_id: int, polygon_points: np.ndarray) -> str:
    """
    Format polygon points back to YOLO segmentation label format
    
    Args:
        class_id: Class ID
        polygon_points: Array of shape (n_points, 2)
        
    Returns:
        Formatted label line
    """
    coords_flat = polygon_points.flatten()
    coords_str = ' '.join(f"{coord:.6f}" for coord in coords_flat)
    return f"{class_id} {coords_str}"

def parse_label_file(label_path: str) -> List[Tuple[int, np.ndarray]]:
    """
    Parse entire YOLO segmentation label file
    
    Args:
        label_path: Path to label file
        
    Returns:
        List of (class_id, polygon_points) tuples
    """
    labels = []
    try:
        with open(label_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    class_id, polygon_points = parse_yolo_segmentation_label(line)
                    labels.append((class_id, polygon_points))
                except ValueError as e:
                    print(f"Warning: Line {line_num} in {label_path}: {e}")
    except FileNotFoundError:
        print(f"Warning: Label file not found: {label_path}")
    
    return labels

def save_label_file(label_path: str, labels: List[Tuple[int, np.ndarray]]):
    """
    Save labels to YOLO segmentation format file
    
    Args:
        label_path: Output path for label file
        labels: List of (class_id, polygon_points) tuples
    """
    with open(label_path, 'w') as f:
        for class_id, polygon_points in labels:
            label_line = format_yolo_segmentation_label(class_id, polygon_points)
            f.write(label_line + '\n')