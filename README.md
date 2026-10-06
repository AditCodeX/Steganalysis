# Steganalysis Toolkit

An open-source digital image steganography and forensic steganalysis suite built with Python, NumPy, and Scikit-Learn. Provides end-to-end tooling for sequential Least Significant Bit (LSB) message injection, bit-plane visual attack inspection, and statistical machine learning classification.

---

## Architecture Overview

```
Steganalysis/
├── stego_engine.py      # LSB Injector & Extractor (32-bit length prefix)
├── visualize_lsb.py     # LSB Bit-Plane Visual Attack analyzer
├── utils.py             # 10-dimensional spatial & statistical feature extraction
├── buat_dataset.py      # Batch feature extraction from clean/stego image folders
├── create_samples.py    # Synthetic dataset generator for rapid testing
├── latih_model.py       # Trains Decision Tree & Gaussian Naive Bayes models
├── prediksi.py          # Classifies unseen images as Clean or Stego
├── demo.py              # Automated end-to-end workflow demonstration
├── requirements.txt     # Python dependencies
└── LICENSE              # GNU General Public License v3.0
```

---

## Features

1. **Deterministic LSB Stego Engine (`stego_engine.py`):**
   - Embeds utf-8 string payloads sequentially into image RGB channels.
   - Prepends a 32-bit binary length header to avoid delimiter corruption or string termination artifacts.
   - Extracts and reconstructs messages deterministically.

2. **LSB Visual Attack (`visualize_lsb.py`):**
   - Isolates the Least Significant Bit plane (`pixel % 2`).
   - Normalizes binary bit values ($0 \rightarrow 0$, $1 \rightarrow 255$) to highlight high-frequency noise introduced by secret payloads.
   - Generates side-by-side diagnostic plots of original carriers vs bit planes.

3. **Multi-Dimensional Statistical Feature Extraction (`utils.py`):**
   - Computes per-channel LSB mean and standard deviation across R, G, B planes.
   - Measures horizontal and vertical bit transition rates ($\Delta LSB$) to capture spatial correlation decay in modified pixels.

4. **Machine Learning Classifiers (`latih_model.py` & `prediksi.py`):**
   - Implements supervised classification using **Decision Trees** and **Gaussian Naive Bayes**.
   - Serializes trained model weights via `joblib`.

---

## Quickstart & Demo

Run the automated demonstration to generate sample datasets, train models, execute a visual attack, and verify decoding in a single command:

```bash
git clone https://github.com/AditCodeX/Steganalysis.git
cd Steganalysis
pip install -r requirements.txt
python demo.py
```

---

## Command Line Usage

### 1. Hide a Message in an Image (Encode)
```bash
python stego_engine.py encode -i carrier.png -m "Classified Payload 0x4F" -o stego_output.png
```

### 2. Extract a Hidden Message (Decode)
```bash
python stego_engine.py decode -i stego_output.png
```

### 3. Visual LSB Attack Inspection
```bash
python visualize_lsb.py -i stego_output.png -o visual_report.png
```

### 4. Machine Learning Steganalysis Pipeline

1. **Generate Synthetic Training Samples:**
   ```bash
   python create_samples.py
   ```
2. **Extract Features to Dataset:**
   ```bash
   python buat_dataset.py
   ```
3. **Train Models:**
   ```bash
   python latih_model.py
   ```
4. **Predict an Unseen Target Image:**
   ```bash
   python prediksi.py target_image.png
   ```

---

## Dependencies

- Python 3.9+
- `Pillow`
- `numpy`
- `scikit-learn`
- `joblib`
- `matplotlib`
- `scipy`

---

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
