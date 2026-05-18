#!/usr/bin/env python3
"""
preprocess_bossbase.py

Juanli Sun, Yan Ke, Minqing Zhang, Shijun Xiang 2025.

"""

import cv2 as cv
import os

def convert_pgm_to_png_512grayscale(input_dir, output_dir):
    """
    Batch convert PGM files in data/raw to 512×512 grayscale PNG format,
    output to data/baseline while preserving the original directory structure.

    Key features:
    - Force grayscale mode for all outputs
    - Resize all images to 512×512 resolution (bilinear interpolation)
    - Recursively process subdirectories
    - Error handling for corrupted files or non-standard PGM formats
    """

    # Validate input directory existence
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist! Please check the path.")
        return

    pgm_files = [f for f in os.listdir(input_dir) if f.endswith('.pgm')]

    if not pgm_files:
        print(f"Error: No .pgm files found in {input_dir}!")
        print("Please make sure the directory contains .pgm files before running this script.")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Statistics variables
    converted_count = 0
    failed_files = []
    target_resolution = (512, 512)  # Fixed 512×512 resolution

    # Traverse input directory (recursive)
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            # Filter PGM files (case-insensitive)
            if file.lower().endswith('.pgm'):
                # Build full path for input PGM file
                pgm_file_path = os.path.join(root, file)
                # Extract filename without extension
                filename = os.path.splitext(file)[0]
                png_filename = f"{filename}.png"

                # Calculate relative path to preserve directory structure
                relative_path = os.path.relpath(root, input_dir)
                png_output_dir = os.path.join(output_dir, relative_path)
                os.makedirs(png_output_dir, exist_ok=True)
                png_file_path = os.path.join(png_output_dir, png_filename)

                try:
                    # Step 1: Read PGM file in grayscale mode (force single channel)
                    img = cv.imread(pgm_file_path, cv.IMREAD_GRAYSCALE)
                    if img is None:
                        raise ValueError("Failed to read PGM file (corrupted or non-standard format)")

                    # Step 2: Resize image to 512×512 (bilinear interpolation for grayscale optimization)
                    img_resized = cv.resize(img, target_resolution, interpolation=cv.INTER_LINEAR)

                    # Step 3: Save as grayscale PNG
                    cv.imwrite(png_file_path, img_resized)

                    converted_count += 1
                    print(f" Converted successfully: {pgm_file_path} -> {png_file_path}")

                except Exception as e:
                    failed_files.append((pgm_file_path, str(e)))
                    print(f" Conversion failed: {pgm_file_path} | Error: {e}")

    # Print conversion summary
    print("\n===== Conversion Complete =====")
    print(f" Total converted successfully: {converted_count} files")
    if failed_files:
        print(f" Total failed conversions: {len(failed_files)} files:")
        for file_path, error in failed_files:
            print(f"  - {file_path}: {error}")
    else:
        print(" All PGM files were converted successfully!")


if __name__ == "__main__":
    # Execute conversion function directly
    input_dir = "data/raw"
    output_dir = "data/baseline"
    convert_pgm_to_png_512grayscale(input_dir, output_dir)
