#!/usr/bin/env python3
"""
test_correlation_map_2000.py

Juanli Sun, Yan Ke, Minqing Zhang, Shijun Xiang 2025.

"""

import os
import sys
import numpy as np
import cv2
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

# Read the image and convert it to grayscale
file_to_read =  'data/img/Med2_enc.png'
if not os.path.exists(file_to_read):
    print(f"ERROR: Image file '{file_to_read}' not found.")
    sys.exit(1)
image = cv2.imread(file_to_read, cv2.IMREAD_GRAYSCALE)

# Get the width and height of the image
height, width = image.shape

# Correlation of horizontally adjacent pixels
def horizontal_correlation(image):
    correlations = []
    for y in range(height):
        for x in range(width - 1):  # Ignore the rightmost column
            pixel1 = image[y, x]
            pixel2 = image[y, x + 1]
            correlations.append((pixel1, pixel2))
    return correlations

# Correlation of vertically adjacent pixels
def vertical_correlation(image):
    correlations = []
    for y in range(height - 1):  # Ignore the bottommost row
        for x in range(width):
            pixel1 = image[y, x]
            pixel2 = image[y + 1, x]
            correlations.append((pixel1, pixel2))
    return correlations

# Correlation of adjacent pixels along the main diagonal (top-left to bottom-right)
def diagonal_1_correlation(image):
    correlations = []
    for y in range(height - 1):  # Ignore the bottommost row
        for x in range(width - 1):  # Ignore the rightmost column
            pixel1 = image[y, x]
            pixel2 = image[y + 1, x + 1]
            correlations.append((pixel1, pixel2))
    return correlations

# Correlation of adjacent pixels along the anti-diagonal (top-right to bottom-left)
def diagonal_2_correlation(image):
    correlations = []
    for y in range(1, height):  # Ignore the topmost row
        for x in range(width - 1):  # Ignore the rightmost column
            pixel1 = image[y, x + 1]
            pixel2 = image[y - 1, x]
            correlations.append((pixel1, pixel2))
    return correlations

# Calculate all correlations in each direction
horizontal_pixels = horizontal_correlation(image)
vertical_pixels = vertical_correlation(image)
diagonal_1_pixels = diagonal_1_correlation(image)
diagonal_2_pixels = diagonal_2_correlation(image)

# Randomly sample 2000 pairs of pixels
def random_sample(correlations, sample_size=2000):
    # Convert the list of tuples to a numpy array and ensure it is one-dimensional
    correlations_array = np.array(correlations)
    return correlations_array[np.random.choice(correlations_array.shape[0], size=sample_size, replace=False)]

# Calculate and plot the scatter plot
def plot_correlation(pixels, title,xlabel,ylabel):
    x = pixels[:, 0]  # First column
    y = pixels[:, 1]  # Second column
    corr, _ = pearsonr(x, y)

    plt.figure(figsize=(6, 6))
    plt.scatter(x, y, alpha=0.5)
    plt.title(f'{title} (Pearson Correlation: {corr:.2f})')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.axis('equal')
    plt.grid()
    plt.show()

# Random sampling and plotting
plot_correlation(random_sample(horizontal_pixels), 'horizontal','(x,y)','(x+1,y)')
plot_correlation(random_sample(vertical_pixels), 'vertical','(x,y)','(x,y+1)')
plot_correlation(random_sample(diagonal_1_pixels), 'main_diagonal','(x,y)','(x+1,y+1)')
plot_correlation(random_sample(diagonal_2_pixels), 'anti_diagonal','(x,y)','(x+1,y-1)')
