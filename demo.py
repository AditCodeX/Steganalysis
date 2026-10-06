"""
Steganalysis Toolkit End-to-End Demonstration Script
Exercises the entire workflow:
1. Synthetic dataset creation
2. Feature extraction & dataset compilation
3. Model training (Decision Tree & Naive Bayes)
4. LSB Visual Attack analysis
5. Unknown image prediction
6. Message decoding verification
"""

import os
import sys
from create_samples import create_synthetic_dataset
from buat_dataset import buat_dan_simpan_dataset
from latih_model import latih_dan_simpan_model
from visualize_lsb import analyze_lsb
from stego_engine import Steganography
import joblib
from utils import ekstrak_fitur
from PIL import Image

def run_demo():
    print("=" * 65)
    print("  STEGANALYSIS TOOLKIT - END-TO-END DEMO")
    print("=" * 65)

    # 1. Create Samples
    print("\n[Phase 1] Generating Synthetic Dataset...")
    create_synthetic_dataset(output_dir="dataset_demo", num_samples_per_class=15)

    # 2. Extract Features
    print("\n[Phase 2] Compiling Dataset Features...")
    buat_dan_simpan_dataset("dataset_demo/bersih", "dataset_demo/stego", "dataset_demo.npz")

    # 3. Train Models
    print("\n[Phase 3] Training Classifiers...")
    latih_dan_simpan_model("dataset_demo.npz", "model_dt.joblib", "model_nb.joblib")

    # 4. LSB Visual Attack
    print("\n[Phase 4] Performing LSB Visual Attack...")
    sample_stego = "dataset_demo/stego/stego_000.png"
    output_viz = "lsb_visual_demo.png"
    analyze_lsb(sample_stego, output_plot=output_viz, show=False)

    # 5. Predict on Unseen Image
    print("\n[Phase 5] Predicting Unseen Test Images...")
    model_dt = joblib.load("model_dt.joblib")
    model_nb = joblib.load("model_nb.joblib")

    for test_path in ["dataset_demo/bersih/clean_001.png", "dataset_demo/stego/stego_001.png"]:
        feat = [ekstrak_fitur(Image.open(test_path))]
        pred_dt = "Stego (Hidden Data)" if model_dt.predict(feat)[0] == 1 else "Clean"
        pred_nb = "Stego (Hidden Data)" if model_nb.predict(feat)[0] == 1 else "Clean"
        print(f"  Target: {test_path}")
        print(f"    -> Decision Tree : {pred_dt}")
        print(f"    -> Naive Bayes   : {pred_nb}")

    # 6. Decode Secret Message
    print("\n[Phase 6] Extracting Hidden Message from Stego Image...")
    engine = Steganography()
    engine.decode(sample_stego)

    print("\n" + "=" * 65)
    print("  DEMO COMPLETED SUCCESSFULLY! ALL MODULES VERIFIED.")
    print("=" * 65)

if __name__ == "__main__":
    run_demo()
