import os
import shutil
import argparse
import yaml

def directory_check(path):
    if not os.path.exists(path):
        os.makedirs(path)

def merge_datasets(input_datasets, output_dataset):
    """
    Merges multiple YOLO segmentation datasets into one.

    :param input_datasets: A list of paths to the input dataset directories.
    :param output_dataset: The path to the output dataset directory.
    """
    print(f"Creating output directory: {output_dataset}")
    directory_check(output_dataset)

    # Define the standard subdirectories
    SUBDIRS = ['train', 'valid', 'test']
    CONTENT_FOLDERS = ['images', 'labels']

    # Copy data.yaml from the first dataset
    # Assuming the yaml file is compatible across all datasets being merged.
    first_yaml_path = os.path.join(input_datasets[0], 'data.yaml')
    if os.path.exists(first_yaml_path):
        shutil.copy2(first_yaml_path, output_dataset)
        print(f"Copied data.yaml from {input_datasets[0]}")
    else:
        print(f"Warning: data.yaml not found in {input_datasets[0]}. You may need to create it manually.")


    for subdir in SUBDIRS:
        output_images_folder = os.path.join(output_dataset, subdir, 'images')
        output_labels_folder = os.path.join(output_dataset, subdir, 'labels')

        # Create the subdirectories in the output folder
        directory_check(output_images_folder)
        directory_check(output_labels_folder)

        for dataset in input_datasets:
            input_images_folder = os.path.join(dataset, subdir, 'images')
            input_labels_folder = os.path.join(dataset, subdir, 'labels')

            # Copy images
            if os.path.exists(input_images_folder):
                print(f"Copying images from {input_images_folder} to {output_images_folder}")
                for filename in os.listdir(input_images_folder):
                    shutil.copy2(os.path.join(input_images_folder, filename), output_images_folder)
            else:
                print(f"Info: Directory not found, skipping: {input_images_folder}")


            # Copy labels
            if os.path.exists(input_labels_folder):
                print(f"Copying labels from {input_labels_folder} to {output_labels_folder}")
                for filename in os.listdir(input_labels_folder):
                    shutil.copy2(os.path.join(input_labels_folder, filename), output_labels_folder)
            else:
                 print(f"Info: Directory not found, skipping: {input_labels_folder}")


    print("\nMerge complete.")
    print(f"The merged dataset is located at: {output_dataset}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple YOLO segmentation datasets.")
    parser.add_argument('--inputs', nargs='+', required=True, help='List of input dataset directories.')
    parser.add_argument('--output', type=str, required=True, help='Output dataset directory.')
    
    args = parser.parse_args()
    
    merge_datasets(args.inputs, args.output)
