#!/usr/bin/env python3
"""
YOLO Segmentation Dataset Rotation Tool

This script rotates YOLO segmentation datasets (images and polygon labels) 
by specified angles while maintaining proper coordinate transformations.

Usage:
    python rotate_seg_dataset.py --input /path/to/dataset --output /path/to/output --angle 90 [--expand]

Author: AI Assistant
"""

import os
import argparse
from pathlib import Path
from tqdm import tqdm

from utils import (
    parse_label_file,
    save_label_file,
    rotate_polygon,
    rotate_polygon_with_bounds,
    filter_valid_polygons,
    load_image,
    save_image,
    rotate_image,
    rotate_image_bound,
    get_dataset_structure,
    create_output_directories,
    copy_yaml_file,
    get_corresponding_files
)

def rotate_dataset_split(input_path: str, output_path: str, split: str,
                        angle: float, expand: bool = False, suffix: str = None):
    """
    Rotate a single dataset split (train/valid/test)
    
    Args:
        input_path: Input dataset root path
        output_path: Output dataset root path
        split: Dataset split name (train/valid/test)
        angle: Rotation angle in degrees (positive = counter-clockwise)
        expand: Whether to expand canvas to avoid cropping
        suffix: Suffix to add to output files
    """
    print(f"Processing {split} split...")
    
    images_dir = os.path.join(input_path, split, 'images')
    labels_dir = os.path.join(input_path, split, 'labels')
    
    output_images_dir = os.path.join(output_path, split, 'images')
    output_labels_dir = os.path.join(output_path, split, 'labels')
    
    # Get corresponding image and label files
    file_pairs = get_corresponding_files(images_dir, labels_dir)
    
    if not file_pairs:
        print(f"No matching image-label pairs found in {split} split")
        return
    
    # Process each image-label pair
    for image_path, label_path in tqdm(file_pairs, desc=f"Rotating {split}"):
        try:
            # Load image
            image = load_image(image_path)
            if image is None:
                continue
            
            # Rotate image
            if expand:
                rotated_image = rotate_image_bound(image, angle)
                new_shape = rotated_image.shape[:2]  # (height, width)
            else:
                rotated_image = rotate_image(image, angle)
                new_shape = image.shape[:2]
            
            # Parse and rotate labels
            labels = parse_label_file(label_path)
            rotated_labels = []
            
            for class_id, polygon_points in labels:
                if expand:
                    rotated_polygon, _ = rotate_polygon_with_bounds(
                        polygon_points, angle, image.shape[:2]
                    )
                else:
                    rotated_polygon = rotate_polygon(polygon_points, angle)
                
                rotated_labels.append((class_id, rotated_polygon))
            
            # Filter out invalid polygons after transformation
            rotated_labels = filter_valid_polygons(rotated_labels)
            
            # Generate output file names
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            image_ext = os.path.splitext(image_path)[1]
            
            if suffix is None:
                if expand:
                    output_suffix = f"rot_{int(angle)}_exp"
                else:
                    output_suffix = f"rot_{int(angle)}"
            else:
                output_suffix = suffix
            
            output_image_name = f"{image_name}_{output_suffix}{image_ext}"
            output_label_name = f"{image_name}_{output_suffix}.txt"
            
            output_image_path = os.path.join(output_images_dir, output_image_name)
            output_label_path = os.path.join(output_labels_dir, output_label_name)
            
            # Save rotated image and labels
            save_image(rotated_image, output_image_path)
            if rotated_labels:  # Only save if there are valid labels
                save_label_file(output_label_path, rotated_labels)
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            continue

def main():
    parser = argparse.ArgumentParser(
        description='Rotate YOLO segmentation dataset (images and polygon labels)'
    )
    parser.add_argument('--input', type=str, required=True,
                       help='Input dataset directory path')
    parser.add_argument('--output', type=str, required=False,
                       help='Output dataset directory path (default: input_path_rot_ANGLE)')
    parser.add_argument('--angle', type=float, required=True,
                       help='Rotation angle in degrees (positive = counter-clockwise)')
    parser.add_argument('--expand', action='store_true',
                       help='Expand canvas to avoid cropping (default: False)')
    parser.add_argument('--suffix', type=str, default=None,
                       help='Custom suffix for output files')
    
    args = parser.parse_args()
    
    # Validate input path
    if not os.path.exists(args.input):
        print(f"Error: Input path does not exist: {args.input}")
        return
    
    # Validate angle
    if args.angle == 0:
        print("Warning: Rotation angle is 0, no transformation needed")
        return
    
    # Set default output path
    if args.output is None:
        if args.expand:
            args.output = f"{args.input}_rot_{int(args.angle)}_exp"
        else:
            args.output = f"{args.input}_rot_{int(args.angle)}"
    
    print(f"Input dataset: {args.input}")
    print(f"Output dataset: {args.output}")
    print(f"Rotation angle: {args.angle}°")
    print(f"Expand canvas: {args.expand}")
    if args.suffix:
        print(f"Custom suffix: {args.suffix}")
    
    # Get dataset structure
    structure = get_dataset_structure(args.input)
    available_splits = [split for split, data in structure.items()
                       if data['images'] or data['labels']]
    
    if not available_splits:
        print("Error: No valid dataset splits found")
        return
    
    print(f"Found splits: {available_splits}")
    
    # Create output directories
    create_output_directories(args.output, available_splits)
    
    # Process each split
    for split in available_splits:
        if structure[split]['images']:
            rotate_dataset_split(args.input, args.output, split,
                               args.angle, args.expand, args.suffix)
        else:
            print(f"Skipping {split} split (no images found)")
    
    # Copy configuration files
    copy_yaml_file(args.input, args.output)
    
    print(f"\nDataset rotation completed!")
    print(f"Output saved to: {args.output}")

if __name__ == "__main__":
    main()