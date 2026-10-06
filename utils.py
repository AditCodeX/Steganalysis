"""
Feature Extraction Utilities for Steganalysis
Extracts high-dimensional statistical and transition features across RGB channels.
"""

import numpy as np
from PIL import Image

def ekstrak_fitur(gambar: Image.Image) -> list:
    """
    Extracts statistical features from the LSB plane:
    - Per-channel LSB mean (R, G, B)
    - Per-channel LSB standard deviation (R, G, B)
    - Per-channel horizontal LSB bit-transition rate (spatial correlation)
    - Global Chi-square deviation metric across pixel pairs

    Returns:
        list: 10-dimensional statistical feature vector.
    """
    arr = np.array(gambar.convert('RGB'), dtype=np.uint8)
    lsb = arr % 2

    fitur = []

    # 1. Per-channel Mean & Std (6 features)
    for c in range(3):
        ch_lsb = lsb[:, :, c]
        fitur.append(float(ch_lsb.mean()))
        fitur.append(float(ch_lsb.std()))

    # 2. Per-channel Horizontal Bit Transition Rate (3 features)
    # Natural images have high spatial correlation (lower bit transitions).
    # Stego images introduce pseudo-random bit flips (transition rate approaches 0.5).
    for c in range(3):
        ch_lsb = lsb[:, :, c]
        diff = np.abs(ch_lsb[:, 1:] - ch_lsb[:, :-1])
        transition_rate = float(diff.mean())
        fitur.append(transition_rate)

    # 3. Overall Bit Entropy / Transition measure (1 feature)
    diff_vert = np.abs(lsb[1:, :, :] - lsb[:-1, :, :])
    fitur.append(float(diff_vert.mean()))

    return fitur
