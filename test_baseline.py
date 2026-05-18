#!/usr/bin/env python3
"""
test_baseline.py

Juanli Sun, Yan Ke, Minqing Zhang, Shijun Xiang 2025.

"""

import cv2 as cv
import numpy as np
import os
from utils.calc_distortion import calculate_psnr,calculate_ssim,calculate_nae,calculate_kl_divergence,calculate_cross_entropy

filename = 'data/img/'
compare = 'data/baseline'
baseimg = 'House.png'
img = cv.imread(filename + baseimg,0)
psnr = []
ssim = []

png_files = []
for file in os.listdir(compare):
    if file.endswith('.png') and file != baseimg:
        png_files.append(file)

if not png_files:
    print("Error: No PNG files found in the directory!")
    print("Please run 'python utils/preprocess_bossbase.py' first to generate PNG files")
    exit(1)

print(f"Found {len(png_files)} PNG files")

for idx, file in enumerate(png_files, start=1):
    compare_path = os.path.join(compare, file)
    img1 = cv.imread(compare_path, 0)
    if img1 is None:
        print(f"Warning: Failed to read file {file}, skipping")
        continue

    psnr1 = calculate_psnr(img,img1)
    ssim1 = calculate_ssim(img, img1)
    psnr.append(psnr1)
    ssim.append(ssim1)
    print(f' deal with the {idx} -th file: {file}')

print(f'psnr baseline:{str(np.mean(psnr))}')
print(f'ssim baseline:{str(np.mean(ssim))}')
