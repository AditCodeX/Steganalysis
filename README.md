# Steganalysis Toolkit

<div align="center">

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![NumPy](https://img.shields.io/badge/numpy-2.0+-green.svg)](https://numpy.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)
[![Pillow](https://img.shields.io/badge/pillow-10.0+-yellow.svg)](https://python-pillow.org/)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[![Security Focus: Forensics](https://img.shields.io/badge/domain-digital%20forensics-red.svg)](https://github.com/AditCodeX)

**An open-source digital image steganography engine and forensic steganalysis suite.**  
*Covers offensive sequential Least Significant Bit (LSB) embedding and defensive forensic countermeasures (visual bit-plane attacks and supervised machine learning classification).*

</div>

---

## 1. Project Overview

The **Steganalysis Toolkit** provides a complete, dual-sided framework for analyzing digital image steganography:

1. **Offensive Pipeline (Covert Communication):** Embeds and recovers arbitrary UTF-8 text data inside lossless carrier images (PNG) using sequential LSB manipulation. Uses a deterministic 32-bit length prefix framing technique to eliminate payload corruption.
2. **Defensive Pipeline (Forensic Steganalysis):** Detects covert channels through both qualitative visual inspection (bit-plane slicing) and quantitative statistical analysis (12-dimensional spatial feature extraction combined with supervised Decision Tree and Gaussian Naive Bayes classifiers).

### Problem Addressed
Standard sequential LSB embedding introduces subtle pixel-level modifications that remain imperceptible to the human eye. However, the insertion of pseudo-random binary data disrupts the natural statistical and spatial correlation between neighboring pixels. This toolkit formalizes these anomalies into mathematically verifiable indicators, enabling automated detection of stego images with high classification accuracy.

---

## 2. Technical Architecture & How It Works

The system operates across two distinct pipelines:

```
====================================================================================================
                                    PIPELINE 1: STEGANOGRAPHY
====================================================================================================

  [Carrier Image] + [Secret Message]
          |
          v
  [stego_engine.py]
          |
          +---> 1. Convert UTF-8 Text to Bitstream (8 bits / byte)
          +---> 2. Prepend 32-bit Fixed-Width Binary Length Header
          +---> 3. Sequential Bitwise Masking on RGB Pixels:
                   Pixel' = (Pixel & 0xFE) | Bit
          |
          v
  [Stego Image Output] (Visually Indistinguishable)


====================================================================================================
                                 PIPELINE 2: FORENSIC STEGANALYSIS
====================================================================================================

                     [Suspect Image Under Investigation]
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
  [visualize_lsb.py]                                        [Feature Extraction: utils.py]
  - Bit-Plane Extraction: Pixel % 2                         - Header Bit Densities (32 & 256 bits)
  - Monochrome Scaling: 0 -> 0, 1 -> 255                    - Leading Zero Run Length
  - Visual Artifact Detection                               - Per-Channel LSB Mean & Std Dev (R, G, B)
         |                                                  - Spatial Delta-LSB Transition Rates
         v                                                  - Local Head vs. Tail Discrepancy
  [Dual-Pane Visual Report]                                        |
                                                                   v
                                                            [12D Feature Vector]
                                                                   |
                                                                   v
                                                            [prediksi.py]
                                                            Deserializes trained models:
                                                            - DecisionTreeClassifier (model_dt.joblib)
                                                            - GaussianNB (model_nb.joblib)
                                                                   |
                                                                   v
                                                      Forensic Verdict Output:
                                                      [Clean] vs. [Stego (Hidden Data)]
                                                                   |
                                                     (If Confirmed Stego & Recoverable)
                                                                   v
                                                        [stego_engine.py decode]
                                                        Extracts 32-bit header -> reads L bits
                                                                   v
                                                        [Reconstructed Message]
====================================================================================================
```

---

## 3. How It Works: Component Breakdown

### A. Steganography Engine (`stego_engine.py`)
- **Binary Conversion:** Converts UTF-8 string characters into an 8-bit binary representation.
- **32-Bit Length Prefix Framing:** Avoids null-byte delimiters (`\0`) which frequently corrupt when payloads contain binary zeros. Instead, it measures total bit length $L$ and prepends a 32-bit binary integer (`format(L, '032b')`).
- **Sequential Pixel Substitution:** Modifies the least significant bit of each color channel sequentially starting from coordinate $(0, 0)$:
  $$\text{Pixel}_{\text{stego}} = (\text{Pixel}_{\text{orig}} \ \& \ \text{0xFE}) \ | \ \text{Bit}$$
- **Capacity Guard:** Enforces $\text{Length}_{\text{payload}} \le W \times H \times 3$ to prevent memory corruption or truncation.

### B. Bit-Plane Visual Attack (`visualize_lsb.py`)
- **LSB Plane Isolation:** Applies modulo-2 across all channels:
  $$\text{LSB}(x, y, c) = \text{Pixel}(x, y, c) \pmod 2$$
- **Contrast Normalization:** Scales bits to full 8-bit dynamic range ($0 \rightarrow 0$, $1 \rightarrow 255$).
- **Forensic Diagnostic:** Natural images feature smooth spatial gradients in the LSB plane. Sequentially injected stego images exhibit a distinct horizontal band of uniform high-frequency noise at the top of the image where data bits reside, providing immediate visual proof of tampering.

### C. 12-Dimensional Forensic Feature Extraction (`utils.py`)
Extracts a 12-dimensional numerical vector capturing spatial and statistical shifts:
1. **Header Bit Densities ($F_1, F_2$):** Mean bit density across the first 32 and 256 pixels. Clean natural images have mixed parity ($\approx 0.50$); a 32-bit integer length prefix introduces a dense cluster of leading zero bits.
2. **Leading Zero Run Length ($F_3$):** Consecutive zeros starting from bit 0. A run of 15 to 25 zeros indicates the presence of a 32-bit integer length prefix for typical text lengths.
3. **Channel Moments ($F_4$ to $F_9$):** Global mean and standard deviation of LSBs across individual Red, Green, and Blue planes.
4. **Spatial Bit-Transition Rates ($F_{10}, F_{11}$):** Measures horizontal and vertical adjacent bit flips ($\Delta \text{LSB}$):
   $$\Delta \text{LSB}_{\text{horiz}} = \frac{1}{H(W-1)} \sum_{y=0}^{H-1} \sum_{x=0}^{W-2} |\text{LSB}(y, x+1) - \text{LSB}(y, x)|$$
   *Implemented using `int16` casting to prevent unsigned integer underflow (`0 - 1 = 255`).*
5. **Local Discrepancy Metric ($F_{12}$):** Absolute difference in bit-transition rate between the modified head block (first 1,000 pixels) and untouched carrier tail (last 1,000 pixels):
   $$\delta_{\text{local}} = |\text{Rate}_{\text{head}} - \text{Rate}_{\text{tail}}|$$
   Natural images maintain consistent spatial noise across the canvas ($\delta_{\text{local}} \approx 0$). Sequential stego images show significant disparity.

### D. Supervised Model Training (`latih_model.py`)
- **Stratified Partition:** Splits dataset 80/20 into train/test sets, preserving class distribution.
- **Dual Classifiers:**
  - **Decision Tree (`DecisionTreeClassifier`):** Learns non-linear orthogonal splits based on leading zero counts and local transition discrepancies.
  - **Gaussian Naive Bayes (`GaussianNB`):** Calculates conditional probability densities across statistical moments.
- **Persistence:** Serializes trained model weights via `joblib` into `model_dt.joblib` and `model_nb.joblib`.

### E. Target Inference (`prediksi.py`)
- Ingests suspect target image via CLI.
- Extracts the 12D feature vector in real time.
- Queries both serialized models and outputs individual verdicts (`Bersih` vs `Tersembunyi`).

---

## 4. Repository File Structure

```
Steganalysis/
├── stego_engine.py      # Core LSB encoder and decoder with 32-bit header framing
├── visualize_lsb.py     # LSB bit-plane visual attack extractor & plot generator
├── utils.py             # 12-dimensional spatial & statistical feature extraction
├── buat_dataset.py      # Automated feature matrix builder from image directories
├── create_samples.py    # Synthetic clean/stego dataset generator for test pipelines
├── latih_model.py       # Trains and serializes Decision Tree & Naive Bayes models
├── prediksi.py          # Command-line forensic classifier for target images
├── demo.py              # Single-command end-to-end verification script
├── requirements.txt     # Python runtime dependencies
├── .gitignore           # Ignores compiled artifacts, models, and image outputs
└── LICENSE              # GNU General Public License v3.0
```

---

## 5. Installation & Setup

```bash
# 1. Clone repository
git clone https://github.com/AditCodeX/Steganalysis.git
cd Steganalysis

# 2. Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 6. Command Line Usage

### A. Hide a Secret Message in an Image (Encode)
```bash
python stego_engine.py encode -i input_carrier.png -m "Classified Payload Alpha-01" -o stego_output.png
```

### B. Extract Secret Message from a Stego Image (Decode)
```bash
python stego_engine.py decode -i stego_output.png
```

### C. Perform LSB Visual Attack Inspection
```bash
# Generate side-by-side diagnostic plot and save to file
python visualize_lsb.py -i stego_output.png -o visual_report.png --no-show

# Interactive inspection window
python visualize_lsb.py -i stego_output.png
```

### D. Full Machine Learning Steganalysis Pipeline

```bash
# Step 1: Generate synthetic clean and stego training pairs
python create_samples.py

# Step 2: Extract 12D features and compile to dataset.npz
python buat_dataset.py

# Step 3: Train and evaluate Decision Tree & Naive Bayes classifiers
python latih_model.py

# Step 4: Classify an unknown target image
python prediksi.py target_image.png
```

---

## 7. Verified End-to-End Demo Output

Execute all 6 operational phases in a single automated run:

```bash
python demo.py
```

### Real Execution Log:
```text
=================================================================
  STEGANALYSIS TOOLKIT - END-TO-END DEMO
=================================================================

[Phase 1] Generating Synthetic Dataset...
[*] Generating 15 clean and 15 stego samples in 'dataset_demo'...
[+] Message encoded successfully (72 chars / 576 payload bits) -> dataset_demo\stego\stego_000.png
...
[+] Successfully created sample dataset in 'dataset_demo/'.

[Phase 2] Compiling Dataset Features...
Dataset berhasil dibuat dari 30 gambar dan disimpan di: dataset_demo.npz

[Phase 3] Training Classifiers...
Dataset dimuat. Total sampel: 30. Melatih dengan 24 sampel.
--- Melatih Model Decision Tree ---
Akurasi Decision Tree pada data uji: 100.00%
Model Decision Tree disimpan di: model_dt.joblib
--- Melatih Model Naive Bayes ---
Akurasi Naive Bayes pada data uji: 100.00%
Model Naive Bayes disimpan di: model_nb.joblib

[Phase 4] Performing LSB Visual Attack...
[+] LSB visual analysis saved to: lsb_visual_demo.png

[Phase 5] Predicting Unseen Test Images...
  Target: dataset_demo/bersih/clean_001.png
    -> Decision Tree : Clean
    -> Naive Bayes   : Clean
  Target: dataset_demo/stego/stego_001.png
    -> Decision Tree : Stego (Hidden Data)
    -> Naive Bayes   : Stego (Hidden Data)

[Phase 6] Extracting Hidden Message from Stego Image...
[+] Decoded message (72 chars):
    "CLASSIFIED: Target rendezvous coordinates confirmed at 0x7FA4. [ID:0000]"

=================================================================
  DEMO COMPLETED SUCCESSFULLY! ALL MODULES VERIFIED.
=================================================================
```

---

## 8. Dependencies

- Python 3.9+
- `Pillow >= 10.0.0`
- `numpy >= 1.24.0`
- `scikit-learn >= 1.3.0`
- `joblib >= 1.3.0`
- `matplotlib >= 3.7.0`
- `scipy >= 1.10.0`

---

## 9. Author & License

Developed by **[AditCodeX](https://github.com/AditCodeX)**.  
Licensed under the **[GNU General Public License v3.0](LICENSE)**.
