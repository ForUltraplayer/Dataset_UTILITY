#!/usr/bin/env python3
"""
YOLO Segmentation Dataset Flip Tool

This script flips YOLO segmentation datasets (images and polygon labels) 
horizontally or vertically while maintaining proper coordinate transformations.

Usage:
    python flip_seg_dataset.py --input /path/to/dataset --output /path/to/output [--direction horizontal|vertical]

Author: AI Assistant
"""

import os
import argparse
from pathlib import Path
from tqdm import tqdm

from utils import (
    parse_label_file, 
    save_label_file,
    flip_polygon_horizontal,
    flip_polygon_vertical, 
    filter_valid_polygons,
    load_image,
    save_image,
    flip_image_horizontal,
    flip_image_vertical,
    get_dataset_structure,
    create_output_directories,
    copy_yaml_file,
    get_corresponding_files
)

def flip_dataset_split(input_path: str, output_path: str, split: str, 
                      direction: str = 'horizontal', suffix: str = 'flip'):
    """
    Flip a single dataset split (train/valid/test)
    
    Args:
        input_path: Input dataset root path
        output_path: Output dataset root path  
        split: Dataset split name (train/valid/test)
        direction: Flip direction ('horizontal' or 'vertical')
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
    for image_path, label_path in tqdm(file_pairs, desc=f"Flipping {split}"):
        try:
            # Load and flip image
            image = load_image(image_path)
            if image is None:
                continue
                
            if direction == 'horizontal':
                flipped_image = flip_image_horizontal(image)
            else:  # vertical
                flipped_image = flip_image_vertical(image)
            
            # Parse and flip labels
            labels = parse_label_file(label_path)
            flipped_labels = []
            
            for class_id, polygon_points in labels:
                if direction == 'horizontal':
                    flipped_polygon = flip_polygon_horizontal(polygon_points)
                else:  # vertical
                    flipped_polygon = flip_polygon_vertical(polygon_points)
                
                flipped_labels.append((class_id, flipped_polygon))
            
            # Filter out invalid polygons after transformation
            flipped_labels = filter_valid_polygons(flipped_labels)
            
            # Generate output file names
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            image_ext = os.path.splitext(image_path)[1]
            
            output_image_name = f"{image_name}_{suffix}{image_ext}"
            output_label_name = f"{image_name}_{suffix}.txt"
            
            output_image_path = os.path.join(output_images_dir, output_image_name)
            output_label_path = os.path.join(output_labels_dir, output_label_name)
            
            # Save flipped image and labels
            save_image(flipped_image, output_image_path)
            if flipped_labels:  # Only save if there are valid labels
                save_label_file(output_label_path, flipped_labels)
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            continue

def main():
    parser = argparse.ArgumentParser(
        description='Flip YOLO segmentation dataset (images and polygon labels)'
    )
    parser.add_argument('--input', type=str, required=True,
                       help='Input dataset directory path')
    parser.add_argument('--output', type=str, required=False,
                       help='Output dataset directory path (default: input_path_flip)')
    parser.add_argument('--direction', type=str, choices=['horizontal', 'vertical'], 
                       default='horizontal',
                       help='Flip direction: horizontal (left-right) or vertical (up-down)')
    parser.add_argument('--suffix', type=str, default=None,
                       help='Custom suffix for output files (default: flip_h or flip_v)')
    
    args = parser.parse_args()
    
    # Validate input path
    if not os.path.exists(args.input):
        print(f"Error: Input path does not exist: {args.input}")
        return
    
    # Set default output path
    if args.output is None:
        args.output = f"{args.input}_flip_{args.direction[0]}"
    
    # Set default suffix
    if args.suffix is None:
        args.suffix = f"flip_{args.direction[0]}"
    
    print(f"Input dataset: {args.input}")
    print(f"Output dataset: {args.output}")
    print(f"Flip direction: {args.direction}")
    print(f"File suffix: {args.suffix}")
    
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
            flip_dataset_split(args.input, args.output, split, 
                             args.direction, args.suffix)
        else:
            print(f"Skipping {split} split (no images found)")
    
    # Copy configuration files
    copy_yaml_file(args.input, args.output)
    
    print(f"\nDataset flip completed!")
    print(f"Output saved to: {args.output}")

if __name__ == "__main__":
    main()