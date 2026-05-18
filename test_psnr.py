#!/usr/bin/env python3
"""
test_psnr.py

Juanli Sun, Yan Ke, Minqing Zhang, Shijun Xiang 2025.

"""

import cv2 as cv
import numpy as np
import os
import sys
from utils.calc_distortion import calculate_psnr,calculate_ssim

filename = 'data/img/Med2'
file_to_read = filename if filename.lower().endswith('.png') else filename + '.png'
file_to_read_rec = filename + '_rec.png'
if not os.path.exists(file_to_read):
    print(f"ERROR: Image file '{file_to_read}' not found.")
    sys.exit(1)
if not os.path.exists(file_to_read_rec):
    print(f"ERROR: Image file '{file_to_read_rec}' not found.")
    sys.exit(1)
img = cv.imread(file_to_read, 0)
img1 = cv.imread(file_to_read_rec,0)

psnr1 = calculate_psnr(img,img1)
ssim1 = calculate_ssim(img,img1)
print(f'psnr1: {psnr1}')
print(f'ssim1: {ssim1}')
