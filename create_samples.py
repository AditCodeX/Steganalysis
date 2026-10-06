"""
Synthetic Sample Dataset Generator for Steganalysis Testing
Generates smooth gradient and textured natural-like images for clean (label 0)
and stego (label 1) classes to enable end-to-end model training and testing.
"""

import os
import numpy as np
from PIL import Image
from stego_engine import Steganography

MESSAGES = [
    "CLASSIFIED: Target rendezvous coordinates confirmed at 0x7FA4.",
    "CONFIDENTIAL: Vulnerability identified in firmware bootloader v2.1.",
    "TOP_SECRET: Symmetric encryption key rotation scheduled for 00:00 UTC.",
    "AditCodeX Security Research Lab - Sample Stego Payload.",
    "UNESCO Hall of Fame Responsible Disclosure Proof of Concept.",
    "Red Teaming Operation Payload - Active Defense Bypass."
]

def generate_carrier_image(width: int = 128, height: int = 128, seed: int = 42) -> Image.Image:
    """Generates a natural-like image with smooth color gradients and subtle noise."""
    np.random.seed(seed)
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)

    # Smooth multi-channel gradients
    r = (np.sin(xx * 3.14) * 200 + 40).astype(np.uint8)
    g = (np.cos(yy * 3.14) * 200 + 40).astype(np.uint8)
    b = ((xx + yy) / 2 * 220 + 30).astype(np.uint8)

    arr = np.stack([r, g, b], axis=2)
    # Add subtle natural texture noise (even parity preference typical of natural photos)
    noise = (np.random.normal(0, 3, (height, width, 3))).astype(np.int16)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return Image.fromarray(arr)

def create_synthetic_dataset(output_dir: str = "dataset", num_samples_per_class: int = 20):
    """Generates clean and stego image datasets."""
    dir_bersih = os.path.join(output_dir, "bersih")
    dir_stego = os.path.join(output_dir, "stego")

    os.makedirs(dir_bersih, exist_ok=True)
    os.makedirs(dir_stego, exist_ok=True)

    engine = Steganography()

    print(f"[*] Generating {num_samples_per_class} clean and {num_samples_per_class} stego samples in '{output_dir}'...")

    for i in range(num_samples_per_class):
        img = generate_carrier_image(128, 128, seed=100 + i)
        path_bersih = os.path.join(dir_bersih, f"clean_{i:03d}.png")
        img.save(path_bersih)

        path_stego = os.path.join(dir_stego, f"stego_{i:03d}.png")
        msg = MESSAGES[i % len(MESSAGES)] + f" [ID:{i:04d}]"
        engine.encode(path_bersih, msg, path_stego)

    print(f"[+] Successfully created sample dataset in '{output_dir}/'.")

if __name__ == "__main__":
    create_synthetic_dataset()
