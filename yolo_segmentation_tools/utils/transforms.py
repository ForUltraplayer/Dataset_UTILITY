import numpy as np
from typing import List, Tuple
import math

def flip_polygon_horizontal(polygon_points: np.ndarray) -> np.ndarray:
    """
    Flip polygon points horizontally (left-right)
    
    Args:
        polygon_points: Array of shape (n_points, 2) with normalized coordinates [0, 1]
        
    Returns:
        Flipped polygon points
    """
    flipped = polygon_points.copy()
    flipped[:, 0] = 1.0 - flipped[:, 0]  # x' = 1 - x
    return flipped

def flip_polygon_vertical(polygon_points: np.ndarray) -> np.ndarray:
    """
    Flip polygon points vertically (up-down)
    
    Args:
        polygon_points: Array of shape (n_points, 2) with normalized coordinates [0, 1]
        
    Returns:
        Flipped polygon points
    """
    flipped = polygon_points.copy()
    flipped[:, 1] = 1.0 - flipped[:, 1]  # y' = 1 - y
    return flipped

def rotate_polygon(polygon_points: np.ndarray, angle_degrees: float) -> np.ndarray:
    """
    Rotate polygon points around the center (0.5, 0.5)
    
    Args:
        polygon_points: Array of shape (n_points, 2) with normalized coordinates [0, 1]
        angle_degrees: Rotation angle in degrees (positive = counter-clockwise)
        
    Returns:
        Rotated polygon points
    """
    if angle_degrees % 360 == 0:
        return polygon_points.copy()
    
    # Convert to radians
    angle_rad = math.radians(angle_degrees)
    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)
    
    # Center point
    center = np.array([0.5, 0.5])
    
    # Translate to origin
    centered_points = polygon_points - center
    
    # Rotation matrix
    rotation_matrix = np.array([
        [cos_theta, -sin_theta],
        [sin_theta, cos_theta]
    ])
    
    # Apply rotation
    rotated_points = np.dot(centered_points, rotation_matrix.T)
    
    # Translate back
    result = rotated_points + center
    
    # Clip to [0, 1] range
    result = np.clip(result, 0.0, 1.0)
    
    return result

def rotate_polygon_with_bounds(polygon_points: np.ndarray, angle_degrees: float, 
                             image_shape: Tuple[int, int]) -> Tuple[np.ndarray, Tuple[int, int]]:
    """
    Rotate polygon points with expanded canvas to avoid clipping
    
    Args:
        polygon_points: Array of shape (n_points, 2) with normalized coordinates [0, 1]
        angle_degrees: Rotation angle in degrees
        image_shape: Original image shape (height, width)
        
    Returns:
        Tuple of (rotated_polygon_points, new_image_shape)
    """
    if angle_degrees % 360 == 0:
        return polygon_points.copy(), image_shape
    
    height, width = image_shape
    angle_rad = math.radians(angle_degrees)
    
    # Calculate new canvas size
    cos_a = abs(math.cos(angle_rad))
    sin_a = abs(math.sin(angle_rad))
    new_width = int(width * cos_a + height * sin_a)
    new_height = int(width * sin_a + height * cos_a)
    
    # Convert normalized coordinates to pixel coordinates
    pixel_points = polygon_points * np.array([width, height])
    
    # Center points for rotation
    old_center = np.array([width / 2, height / 2])
    new_center = np.array([new_width / 2, new_height / 2])
    
    # Translate to origin
    centered_points = pixel_points - old_center
    
    # Apply rotation
    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)
    rotation_matrix = np.array([
        [cos_theta, -sin_theta],
        [sin_theta, cos_theta]
    ])
    
    rotated_points = np.dot(centered_points, rotation_matrix.T)
    
    # Translate to new center
    final_points = rotated_points + new_center
    
    # Normalize to [0, 1] based on new canvas size
    normalized_points = final_points / np.array([new_width, new_height])
    
    # Clip to [0, 1] range
    normalized_points = np.clip(normalized_points, 0.0, 1.0)
    
    return normalized_points, (new_height, new_width)

def filter_valid_polygons(labels: List[Tuple[int, np.ndarray]], 
                         min_area_ratio: float = 0.001) -> List[Tuple[int, np.ndarray]]:
    """
    Filter out polygons that are too small or invalid after transformation
    
    Args:
        labels: List of (class_id, polygon_points) tuples
        min_area_ratio: Minimum area ratio relative to image area
        
    Returns:
        Filtered list of valid labels
    """
    valid_labels = []
    
    for class_id, polygon_points in labels:
        # Check if polygon has at least 3 points
        if len(polygon_points) < 3:
            continue
            
        # Calculate polygon area using shoelace formula
        x = polygon_points[:, 0]
        y = polygon_points[:, 1]
        area = 0.5 * abs(sum(x[i] * y[i + 1] - x[i + 1] * y[i] 
                            for i in range(-1, len(x) - 1)))
        
        # Filter by minimum area
        if area >= min_area_ratio:
            valid_labels.append((class_id, polygon_points))
    
    return valid_labels