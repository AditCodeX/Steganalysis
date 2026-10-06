"""
LSB Visual Attack & Bit-Plane Visualization Module
Visualizes the Least Significant Bit (LSB) plane of images to detect steganographic payloads.
"""

import argparse
import sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def analyze_lsb(image_path: str, output_plot: str = None, show: bool = True):
    """
    Extracts and visualizes the LSB plane of an image.
    Supports RGB, RGBA, and Grayscale modes.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"[-] Error opening image '{image_path}': {e}", file=sys.stderr)
        return False

    # Convert to RGB for standardized analysis
    img_rgb = img.convert('RGB')
    arr = np.array(img_rgb)

    # Extract LSB plane (0 or 1) and scale to 0-255 for display
    lsb_raw = arr % 2
    lsb_scaled = (lsb_raw * 255).astype(np.uint8)

    # Combined grayscale representation across all 3 channels
    lsb_combined = np.mean(lsb_scaled, axis=2).astype(np.uint8)

    # Plot 1: Original vs Combined LSB
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(f"LSB Visual Attack Analysis - {image_path}", fontsize=14, fontweight='bold')

    axes[0].imshow(img_rgb)
    axes[0].set_title("Original Carrier Image")
    axes[0].axis('off')

    axes[1].imshow(lsb_combined, cmap='gray')
    axes[1].set_title("LSB Bit-Plane (0 & 1 scaled to 0-255)")
    axes[1].axis('off')

    plt.tight_layout()

    if output_plot:
        plt.savefig(output_plot, dpi=150, bbox_inches='tight')
        print(f"[+] LSB visual analysis saved to: {output_plot}")

    if show:
        plt.show()

    plt.close()
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LSB Visual Attack Analyzer for Image Steganography.")
    parser.add_argument("-i", "--input", required=True, help="Path to the image to analyze.")
    parser.add_argument("-o", "--output", help="Optional path to save the output plot image.")
    parser.add_argument("--no-show", action="store_true", help="Do not display interactive GUI window.")

    args = parser.parse_args()
    analyze_lsb(args.input, output_plot=args.output, show=not args.no_show)
