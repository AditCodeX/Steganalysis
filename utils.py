"""
Feature Extraction Utilities for Steganalysis
Extracts high-dimensional spatial correlation, bit-transition rates,
and prefix statistics across RGB channels to identify sequential LSB steganography.
"""

import numpy as np
from PIL import Image

def ekstrak_fitur(gambar: Image.Image) -> list:
    """
    Extracts forensic features from the LSB plane:
    1. Header Prefix Density: Mean bit density of first 32 and 256 LSBs.
    2. Leading Zero Run: Counts consecutive leading zeros (typical of 32-bit length prefixes).
    3. Global Channel Statistics: Mean and std-dev across R, G, B planes.
    4. Spatial Bit-Transition Rates: Horizontal and vertical Delta-LSB transition rates.
    5. Local Discrepancy: Difference between modified head transition rate and untouched tail rate.

    Returns:
        list: 12-dimensional statistical feature vector.
    """
    arr = np.array(gambar.convert('RGB'), dtype=np.uint8)
    # Cast to int16 to prevent uint8 underflow when calculating differences
    lsb = (arr % 2).astype(np.int16)
    flat_lsb = lsb.flatten()

    fitur = []

    # 1. Header prefix bit densities
    head_32 = flat_lsb[:32]
    head_256 = flat_lsb[:256]
    fitur.append(float(head_32.mean()))
    fitur.append(float(head_256.mean()))

    # 2. Leading zero run length
    leading_zeros = 0
    for b in head_32:
        if b == 0:
            leading_zeros += 1
        else:
            break
    fitur.append(float(leading_zeros))

    # 3. Global per-channel mean and std (6 features)
    for c in range(3):
        ch = lsb[:, :, c]
        fitur.append(float(ch.mean()))
        fitur.append(float(ch.std()))

    # 4. Global transition rate (horizontal and vertical spatial correlation)
    h_diff = np.abs(lsb[:, 1:, :] - lsb[:, :-1, :]).astype(np.float32)
    v_diff = np.abs(lsb[1:, :, :] - lsb[:-1, :, :]).astype(np.float32)
    fitur.append(float(h_diff.mean()))
    fitur.append(float(v_diff.mean()))

    # 5. Local discrepancy: Head transition rate vs Tail transition rate
    h_trans = np.abs(flat_lsb[1:1000] - flat_lsb[:999]).mean()
    t_trans = np.abs(flat_lsb[-999:] - flat_lsb[-1000:-1]).mean()
    fitur.append(float(abs(h_trans - t_trans)))

    return fitur
