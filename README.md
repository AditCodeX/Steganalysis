# Steganalysis Toolkit

<div align="center">

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![NumPy](https://img.shields.io/badge/numpy-2.0+-green.svg)](https://numpy.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)
[![Pillow](https://img.shields.io/badge/pillow-10.0+-yellow.svg)](https://python-pillow.org/)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[![Security Focus: Forensics](https://img.shields.io/badge/domain-digital%20forensics-red.svg)](https://github.com/AditCodeX)

**An open-source digital image steganography engine and forensic steganalysis suite.**  
Covers offensive sequential LSB embedding and defensive forensic countermeasures (visual bit-plane attacks and supervised ML classification).

<br/>

<!-- System Architecture & Workflow Diagram (Auto-Adapts to Dark / Light GitHub Theme) -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/AditCodeX/Steganalysis/main/assets/architecture_dark.png" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/AditCodeX/Steganalysis/main/assets/architecture_light.png" />
  <img src="https://raw.githubusercontent.com/AditCodeX/Steganalysis/main/assets/architecture_dark.png" alt="Steganalysis Toolkit System Architecture and Data Flow" width="100%" />
</picture>

</div>

---

## 1. System Architecture & Capabilities

| Module | Pipeline Role | Primary Function | Core Technology |
| :--- | :--- | :--- | :--- |
| **`stego_engine.py`** | Offensive / Covert Channel | Embeds & recovers UTF-8 payloads with 32-bit length headers | Bitwise masking `(Pixel & 0xFE) \| bit` |
| **`visualize_lsb.py`** | Defensive / Visual Forensics | Exposes high-frequency noise bands in the LSB plane | Modulo-2 slicing `(Pixel % 2) * 255` |
| **`utils.py`** | Feature Engineering | Extracts 12-dimensional spatial & statistical correlation vectors | $\Delta\text{LSB}$ transitions & prefix density |
| **`latih_model.py`** | Machine Learning | Trains supervised classifiers to distinguish clean vs stego images | Decision Tree & Gaussian Naive Bayes |
| **`prediksi.py`** | Automated Inference | Scans target images and outputs a verified forensic verdict | Serialized `.joblib` model query |

---

## 2. Visual Attack Forensic Demonstration

In sequential LSB steganography, secret payloads are imperceptible to human eyes ($>58\text{ dB}$ PSNR). However, isolating the least significant bit plane ($Bit = \text{Pixel} \pmod 2$) scaled to full contrast ($0 \rightarrow 0, 1 \rightarrow 255$) immediately exposes the injected data as a distinct high-entropy noise band:

<div align="center">
  <img src="https://raw.githubusercontent.com/AditCodeX/Steganalysis/main/assets/visual_attack_comparison.png" alt="LSB Bit-Plane Visual Attack Diagnostic Comparison" width="100%" />
</div>

---

## 3. How It Works (Technical Summary)

### A. 32-Bit Length Prefix Framing
Traditional steganography uses delimiter characters (e.g., `\0` or `EOF`), which trigger premature terminations when payloads contain binary zero bytes. This engine prepends a **32-bit fixed-width binary header** ($L$ bits), enabling deterministic, corruption-free payload recovery:

```text
Bitstream = [32-Bit Header (Length L)] + [UTF-8 Payload (L Bits)]
```

### B. 12-Dimensional Forensic Feature Indicators

Automated detection uses 12 numerical indicators that separate natural image correlation from steganographic tampering:

| Feature Index | Indicator Name | Forensic Significance & Mechanism | Expected Baseline |
| :--- | :--- | :--- | :--- |
| **F1 – F2** | **Header Bit Densities** | Mean bit density across the first 32 and 256 pixels | Clusters of leading zeros vs ~0.50 in natural images |
| **F3** | **Leading Zero Run** | Number of consecutive zero bits starting from bit 0 | 15–25 zeros indicates 32-bit integer length prefix |
| **F4 – F9** | **RGB Channel Moments** | Global mean and standard deviation per channel (R, G, B) | Detects global LSB parity shifts across color planes |
| **F10 – F11** | **Spatial ΔLSB Transitions** | Horizontal & vertical adjacent bit-flip frequency | Random stego flips approach ~0.50 transition rate |
| **F12** | **Local Discrepancy Metric** | Difference between head and tail transition rates (`\|Rate_head - Rate_tail\|`) | ~0 for natural photos; elevated for stego carriers |

---

## 4. Quickstart & Command Line Usage

### Installation
```bash
git clone https://github.com/AditCodeX/Steganalysis.git
cd Steganalysis
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1. Hide & Extract Secret Messages
```bash
# Hide message
python stego_engine.py encode -i carrier.png -m "TOP_SECRET: Coordinates 0x7FA4" -o stego.png

# Extract message
python stego_engine.py decode -i stego.png
```

### 2. Inspect LSB Bit-Plane Visually
```bash
# Generate visual diagnostic plot
python visualize_lsb.py -i stego.png -o visual_report.png --no-show
```

### 3. Machine Learning Forensic Pipeline
```bash
# 1. Generate clean & stego training pairs
python create_samples.py

# 2. Extract 12D features to dataset.npz
python buat_dataset.py

# 3. Train Decision Tree & Naive Bayes classifiers
python latih_model.py

# 4. Predict an unknown target image
python prediksi.py target_image.png
```

### 4. Single-Command Automated Verification
```bash
python demo.py
```

*Executes the entire 6-phase pipeline end-to-end, evaluates test set accuracy (100.0%), and verifies full payload reconstruction.*

---

## 5. Repository Structure

```
Steganalysis/
├── assets/
│   ├── architecture_dark.png        # System architecture diagram (Dark theme)
│   ├── architecture_light.png       # System architecture diagram (Light theme)
│   └── visual_attack_comparison.png # Side-by-side visual attack comparison
├── stego_engine.py                  # LSB encoder & decoder with 32-bit header framing
├── visualize_lsb.py                 # LSB bit-plane visual attack extractor & plot tool
├── utils.py                         # 12D spatial correlation & statistical feature extractor
├── buat_dataset.py                  # Batch feature extractor compiling to dataset.npz
├── create_samples.py                # Synthetic clean & stego dataset generator
├── latih_model.py                   # Model trainer for Decision Tree & Gaussian Naive Bayes
├── prediksi.py                      # Target image classifier CLI
├── demo.py                          # Automated end-to-end verification script
├── requirements.txt                 # Runtime dependencies
└── LICENSE                          # GNU General Public License v3.0
```

---

## 6. Author & License

Developed by **[AditCodeX](https://github.com/AditCodeX)**.  
Licensed under the **[GNU General Public License v3.0](LICENSE)**.
