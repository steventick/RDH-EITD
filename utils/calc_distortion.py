import numpy as np
import cv2
from scipy.stats import entropy

def calculate_psnr( original_image ,reconstructed_image):
    """ Calc PSNR of two images (Peak Signal to Noise Ratio).
    :param original_image: Original image (numpy array).
    :param reconstructed_image: Reconstructed image (numpy array).
    :return: PSNR value.
    """
    original_image = np.array(original_image).astype('float32')
    reconstructed_image = np.array(reconstructed_image).astype('float32')
    mse = np.mean((original_image - reconstructed_image) ** 2)
    if mse == 0:
        # print(f'psnr:'+ 'inf')
        return 'inf'
    max_pixel_value = 255  # For 8-bit images, the maximum pixel value is 255.
    psnr = 10 * np.log10((max_pixel_value ** 2) / mse)
    # print(f'psnr:'+str(psnr))
    return psnr

def calculate_ssim(original_image, reconstructed_image):
    """ Calc SSIM of two images (structural similarity index).
    :param original_image: Original image (numpy array).
    :param reconstructed_image: Reconstructed image (numpy array).
    :return: SSIM value.
    """
    # Ensure image is grayscale
    if len(original_image.shape) == 3:
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    if len(reconstructed_image.shape) == 3:
        reconstructed_image = cv2.cvtColor(reconstructed_image, cv2.COLOR_BGR2GRAY)

    original_image = original_image.astype(np.float64)
    reconstructed_image = reconstructed_image.astype(np.float64)

    mu1 = np.mean(original_image)
    mu2 = np.mean(reconstructed_image)
    sigma1_sq = np.var(original_image)
    sigma2_sq = np.var(reconstructed_image)
    sigma12 = np.cov(original_image.flatten(), reconstructed_image.flatten())[0][1]

    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    ssim_value = (2 * mu1 * mu2 + C1) * (2 * sigma12 + C2) / ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1_sq + sigma2_sq + C2))
    # print(f'ssim:' + str(ssim_value))
    return ssim_value

def calculate_nae(original_image, reconstructed_image):
    """ Calc NAE of two images (normalized absolute error).
    :param original_image: Original image (numpy array).
    :param reconstructed_image: Reconstructed image (numpy array).
    :return: NAE value。
    """
    # Ensure image is grayscale
    if len(original_image.shape) == 3:
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    if len(reconstructed_image.shape) == 3:
        reconstructed_image = cv2.cvtColor(reconstructed_image, cv2.COLOR_BGR2GRAY)

    # Convert to float
    original_image = original_image.astype(np.float64)
    reconstructed_image = reconstructed_image.astype(np.float64)

    # Calc absolute error
    absolute_error = np.abs(original_image - reconstructed_image)

    # Calc NAE
    numerator = np.sum(absolute_error)
    denominator = np.sum(np.abs(original_image))

    # Avoid division by zero
    if denominator == 0:
        return float('inf')  # Or return 0 (per your requirements)

    nae_value = numerator / denominator
    # print(f'nae:' + str(nae_value))
    return nae_value

def calculate_ncc(original_image, reconstructed_image):
    """ Calc NCC of two images (normalized cross-correlation).
    :param original_image: Original image (numpy array).
    :param reconstructed_image: Reconstructed image (numpy array).
    :return: NCC value.
    """
    # Ensure image is grayscale
    if len(original_image.shape) == 3:
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    if len(reconstructed_image.shape) == 3:
        reconstructed_image = cv2.cvtColor(reconstructed_image, cv2.COLOR_BGR2GRAY)

    original_image = original_image.astype(np.float64)
    reconstructed_image = reconstructed_image.astype(np.float64)

    mu_I = np.mean(original_image)
    mu_R = np.mean(reconstructed_image)

    numerator = np.sum((original_image - mu_I) * (reconstructed_image - mu_R))
    denominator = np.sqrt(np.sum((original_image - mu_I) ** 2) * np.sum((reconstructed_image - mu_R) ** 2))

    if denominator == 0:
        return float('inf')

    ncc_value = numerator / denominator
    # print(f'ncc:' + str(ncc_value))
    return ncc_value

def calculate_ER(bits_secret, image):
    """
    Calculate the Embedding Rate (ER) of secret bits in an image.

    Parameters:
    bits_secret (list/array): A sequence of secret bits to be embedded (e.g., binary list [0,1,0,...]).
    image (numpy.ndarray): The carrier image (grayscale image with shape [height, width] or RGB image with shape [height, width, channels]).

    Returns:
    float: The Embedding Rate (ER), calculated as the ratio of the number of secret bits to twice the total number of pixels in the image (2*height*width).
    """
    num_bits_secret = len(bits_secret)
    h,w = image.shape[:2]
    ER = num_bits_secret / (2*h*w)
    return ER


def calculate_kl_divergence(image1, image2, bins=256):
    """
    Calculate the KL divergence of two images.

    Parameters:
    image1 (numpy.ndarray): The first image, a grayscale image or single-channel image.
    image2 (numpy.ndarray): The second image, a grayscale image or single-channel image.
    bins (int): The number of bins in the histogram, default is 256.

    Returns:
    float: The KL divergence of the two images.
    """
    # Convert the image to grayscale (skip if it is already a grayscale image)
    if len(image1.shape) > 2:
        image1 = np.mean(image1, axis=2)
    if len(image2.shape) > 2:
        image2 = np.mean(image2, axis=2)

    # Calculate the histogram of the image
    hist1, _ = np.histogram(image1.ravel(), bins=bins, range=(0, 256), density=True)
    hist2, _ = np.histogram(image2.ravel(), bins=bins, range=(0, 256), density=True)

    # Calculate KL divergence
    kl_divergence = entropy(hist1, hist2)
    # print(f'kl_divergence:' + str(kl_divergence))
    return kl_divergence

def calculate_cross_entropy(image1, image2):
    """
    Calculate the cross entropy of two images

    Parameters:
    image1_path (str): File path of the first image
    image2_path (str): File path of the second image

    Returns:
    float: Cross entropy of the two images
    """
    # Read images
    # image1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    # image2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

    # Ensure the images have the same dimensions
    if image1.shape != image2.shape:
        raise ValueError("The dimensions of the two images must be the same")

    # Convert to float type and normalize to [0, 1]
    image1 = image1.astype(np.float32) / 255.0
    image2 = image2.astype(np.float32) / 255.0

    # Prevent log(0) error
    epsilon = 1e-10

    # Calculate cross entropy
    cross_entropy = -np.sum(image1 * np.log(image2 + epsilon))

    # print(f'cross_entropy:' + str(cross_entropy))

    return cross_entropy