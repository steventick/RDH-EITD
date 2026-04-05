# Reversible Data Hiding in Encrypted Images with Multi-Key Threshold Decryption

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-green.svg)](https://www.python.org/)

A implementation of the paper **“Reversible Data Hiding in Encrypted Images with Dual-Phase Embedding based on Multi-Key Threshold Decryption”**, accepted by *IEEE Transactions on Circuits and Systems for Video Technology*.

This project provides a novel scheme (RDH-EITD) that extends Reversible Data Hiding in Encrypted Images (RDH-EI) to secure multi-party communication scenarios using a `(k, n)`-threshold decryption mechanism.

## ✨ Key Features

*   **Secure Multi-Party Communication**: Shifts from traditional point-to-point to a one-to-many model, mitigating risks of single-point failure and key compromise.
*   **Threshold Decryption**: Employs a `(k, n)`-threshold Paillier cryptosystem, requiring at least `k` out of `n` participants to decrypt, resisting up to `k-1` collusion attacks.
*   **Dual-Phase Embedding**:
    *   **1st-Phase (VE)**: Embeds data (`λ - 9` bpp) verifiable after decryption (content owner authentication).
    *   **2nd-Phase (SB)**: Embeds data (up to 14 bpp) extractable directly from ciphertext (ciphertext distributor authentication).
*   **Formally Proven Security**: Semantic security is reduced to the Decisional Composite Residuosity (DCR) assumption.

## 📂 Project Structure

RDH-EITD/
├── LICENSE # Overall project license (MIT)
├── README.md # This file
├── requirements.txt # Python dependencies
│
├── data/ # Dataset directory (not in version control)
│ ├── img/ # Place original downloaded test images here.
│ ├── baseline/ # Place 999 png images converted from BOSSbase 1.01.
| ├── raw/ # Place 999 pgm images from BOSSbase 1.01.
│
├── dj_mod/ # Modified Damgard-Jurik crypto library
│ ├── LICENSE # ✅ Original library's license (PLEASE PRESERVE)
│ ├── ATTRIBUTION.md # Explanation of modifications
│ ├── init.py # Package exports
│ ├── crypto.py # Core crypto ops (modified for threshold decryption)
│ ├── prime_gen.py # Prime number generation
│ ├── shamir.py # Shamir's Secret Sharing
│ └── utils.py # Utility functions
│
├── utils/ # Some tools implementation
│ ├── calc_distortion.py # Calculate psnr and ssim of two images
│ └── preprocess_bossbase.py # BOSSBase image preprocessing scripts
│
└── rdh-eitd.py # Main RDH-EITD algorithm (KeyGen, Enc, Emb, Dec, Ext, Res)
├── test_baseline.py # Generate the baseline PSNR and SSIM of images that are completely uncorrelated with the test image
├── test_correlation_map_2000.py # Calculate the correlation coefficient of the test image
├── test_generate_image.py # RDH-EITD scheme with generation of images in each phases
├── test_sim_attack.py # Simulates collusion attacks.
└── test_psnr.py # Calculate the distortion of restored image


## 🚀 Getting Started

### 1. Prerequisites

*   **Python 3.6+**
*   We recommend using a virtual environment (`conda` or `venv`).

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/RDH-EITD.git
cd RDH-EITD

# Create and activate a virtual environment (using conda as an example)
conda create -n rdh_eitd python=3.6
conda activate rdh_eitd

# Install required packages
pip install -r requirements.txt
```

**Dependencies** (see `requirements.txt` for precise versions):
- `opencv-python`
- `numpy`
- `gmpy2` (For fast large integer arithmetic)
- `scipy` 
- `matplotlib'`

**Note on `dj_mod`**: The modified cryptographic library is included as source code in the `dj_mod/` directory and does not require a separate `pip install`.

### 3. Dataset Preparation

The experiments in the paper use standard image datasets. Due to size, they are not included in the repository.

1.  Download test images from sources like [USC-SIPI](http://sipi.usc.edu/database/), [BOSSBase](http://agents.fel.cvut.cz/stegodata/), [Oasis dataset](https://sites.wustl.edu/oasisbrains/), [Lung-pet-ct-dx dataset](https://www.cancerimagingarchive.net/collection/lung-pet-ct-dx/).
2.  Select 999 images from BOSSBase in the `data/raw` directory, other images in the `data/img/`.
3.  Run the preprocessing script to convert the pgm format images in the BOSSBase dataset into 512×512 grayscale PNG images.
    ```bash
    python utils/preprocess_bossbase.py
    ```
    Processed images will be saved to `data/baseline/`.

### 4. Running Experiments

To reproduce the main experiments and results from the paper:

```bash
# Run the scheme (keygen, encryption, dual-phase embedding, extraction, decryption, recovery)
python rdh-eitd.py
# Run the program for calculating recovered image distortion 
python test_psnr.py
# Run the program that simulates collusion attacks.
python test_sim_attack.py
# Calculate the baseline PSNR and SSIM of images that are completely uncorrelated with the test image House.png
python test_baseline.py
# Test the correlation coefficient of the test image
python test_correlation_map_2000.py
# Run the scheme with generation of images in each phases.
python test_generate_image.py
```

## 📝 License & Attribution
This project is released under the MIT License. See the LICENSE file for details.

### Important - Third-Party Library:

The dj_mod/ directory contains a modified version of the damgard-jurik homomorphic encryption library.

Original Authors: Nicholas Boucher, Luka Govedič, Pasapol Saowakon, Kyle Swanson

Original Copyright: (c) 2019

Original License: A permissive license functionally identical to the MIT License. The full original license text is preserved in dj_mod/LICENSE. PLEASE DO NOT MODIFY THIS FILE.

Our Modifications: We have modified the library (primarily crypto.py) to implement the share decryption and combining decryption and other features required by our paper. These modifications are detailed in dj_mod/ATTRIBUTION.md.
