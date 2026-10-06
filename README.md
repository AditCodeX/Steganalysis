# Steganalysis Toolkit

An open-source digital image steganography and forensic steganalysis suite built with Python, NumPy, and Scikit-Learn. Provides end-to-end tooling for sequential Least Significant Bit (LSB) message injection, bit-plane visual attack inspection, and statistical machine learning classification.

---

## Architecture Overview

```
Steganalysis/
├── stego_engine.py      # LSB Injector & Extractor (32-bit length prefix framing)
├── visualize_lsb.py     # LSB Bit-Plane Visual Attack analyzer
├── utils.py             # 12-dimensional spatial & statistical feature extraction
├── buat_dataset.py      # Batch feature extraction from clean/stego image directories
├── create_samples.py    # Synthetic dataset generator for rapid testing
├── latih_model.py       # Trains Decision Tree & Gaussian Naive Bayes classifiers
├── prediksi.py          # Classifies unseen images as Clean or Stego (CLI inference)
├── demo.py              # Automated end-to-end workflow demonstration
├── requirements.txt     # Python dependencies
└── LICENSE              # GNU General Public License v3.0
```

---

## End-to-End Project Workflow

The toolkit operates across two primary pipelines: the **Steganography Pipeline** (payload hiding and extraction) and the **Forensic Steganalysis Pipeline** (visual inspection, feature extraction, and machine learning classification).

```
+---------------------------------------------------------------------------------------------------+
|                                  1. STEGANOGRAPHY PIPELINE                                        |
+---------------------------------------------------------------------------------------------------+
  [Carrier Image] + [Secret Message]
          |
          v
  [stego_engine.py] ──> UTF-8 to Binary ──> Prepend 32-bit Length Header ──> Sequential LSB Injection
                                                                                     |
                                                                                     v
                                                                            [Stego Image Output]

+---------------------------------------------------------------------------------------------------+
|                                2. FORENSIC STEGANALYSIS PIPELINE                                  |
+---------------------------------------------------------------------------------------------------+

     [Stego / Unknown Image]
                |
                +───> [visualize_lsb.py] ─────────> LSB Extraction (% 2) ──> Scale (0->0, 1->255)
                |                                                                  |
                |                                                                  v
                |                                                    [Dual-Pane Visual Attack Plot]
                |
                v
        [create_samples.py] ───> Generates Clean Carriers & Stego Pairs
                |
                v
         [buat_dataset.py]
                |
                +───> Calls [utils.py]
                |       ├── Header bit density (first 32 & 256 bits)
                |       ├── Consecutive leading zero run length
                |       ├── Per-channel (R, G, B) LSB Mean & Std Dev
                |       ├── Spatial bit-transition rates (Horizontal & Vertical Delta-LSB)
                |       └── Local discrepancy (Modified Head vs Untouched Tail)
                |
                v
         [dataset.npz] ───> Matrix: X (Samples x 12 Features), y (Labels: 0=Clean, 1=Stego)
                |
                v
        [latih_model.py] ──> 80/20 Stratified Split ──> Trains Decision Tree & Gaussian Naive Bayes
                |                                                 |
                v                                                 v
        [model_dt.joblib]                                 [model_nb.joblib]
                |                                                 |
                +───────────────────────┬─────────────────────────+
                                        |
                                        v
                                 [prediksi.py]
                                        |
                                        v
                           Forensic Output Decision:
                        [Clean] vs [Stego (Hidden Data)]
                                        |
                                        v (If Stego Confirmed)
                             [stego_engine.py decode]
                                        |
                                        v
                            [Reconstructed Secret Message]
```

---

## Detailed Phase-by-Phase Flow Explanation

### Phase 1: Payload Encoding & LSB Injection (`stego_engine.py`)
1. **Binary Serialization:** The secret message string is converted into its UTF-8 byte representation, then converted to an 8-bit binary string.
2. **Length Prefix Framing:** Rather than relying on fragile null-terminator bytes (`\0`) which risk collision with binary data, the engine measures the total payload bit-length $L$ and prepends a **32-bit fixed-width binary header** (`format(L, '032b')`).
3. **Sequential Bit Embedding:** The combined stream (32-bit header + message bits) is sequentially written into the carrier's pixel array starting from coordinates $(0, 0)$. Each color channel's Least Significant Bit is updated using bitwise masking:
   $$\text{Pixel}' = (\text{Pixel} \ \& \ \text{0xFE}) \ | \ \text{Bit}$$
4. **Capacity Enforcement:** Before writing, carrier capacity ($W \times H \times 3$ bits) is validated against payload length to prevent buffer overruns.

### Phase 2: Bit-Plane Visual Attack (`visualize_lsb.py`)
1. **LSB Plane Isolation:** The image is converted to RGB array and filtered using the modulo-2 operation:
   $$\text{LSB}(x, y, c) = \text{Pixel}(x, y, c) \pmod 2$$
2. **Dynamic Range Scaling:** Extracted binary bits ($0$ and $1$) are scaled by $255$ to high-contrast monochrome values ($0 \rightarrow \text{Black}$, $1 \rightarrow \text{White}$).
3. **Diagnostic Rendering:** Generates a dual-pane Matplotlib figure comparing the untouched original image against the high-frequency noise of the LSB plane. In sequential LSB steganography, a distinct textured horizontal band appears at the top rows where data was embedded, contrasting sharply with the natural smooth gradients of the rest of the image.

### Phase 3: Spatial & Statistical Feature Extraction (`utils.py`)
Sequential LSB steganography introduces statistical anomalies into the carrier's bit distribution. `utils.py` computes a **12-dimensional forensic feature vector**:
1. **Header Prefix Density (2 features):** Computes mean bit density over the first 32 and 256 bits. Clean natural images have mixed parity ($\approx 0.50$), whereas the 32-bit integer length prefix introduces a dense cluster of leading zeros for typical message sizes.
2. **Leading Zero Run Length (1 feature):** Counts consecutive zero bits from bit $0$. A run of 15–25 consecutive zeros strongly flags a 32-bit integer length header.
3. **Per-Channel Global Moments (6 features):** Mean and standard deviation of LSBs across individual Red, Green, and Blue channels.
4. **Spatial Bit-Transition Rates (2 features):** Measures the rate at which adjacent bits flip horizontally and vertically ($\Delta \text{LSB}$):
   $$\Delta \text{LSB}_{\text{horiz}} = \frac{1}{H(W-1)} \sum_{y=0}^{H-1} \sum_{x=0}^{W-2} |\text{LSB}(y, x+1) - \text{LSB}(y, x)|$$
   *Note: Calculations use `int16` casting to prevent unsigned integer underflow (`0 - 1 = 255`).*
5. **Local Discrepancy Metric (1 feature):** Computes the absolute difference in transition rate between the modified head block (first 1,000 pixels) and the untouched carrier tail (last 1,000 pixels):
   $$\delta_{\text{local}} = |\text{Rate}_{\text{head}} - \text{Rate}_{\text{tail}}|$$
   Natural images maintain consistent spatial texture throughout, resulting in $\delta_{\text{local}} \approx 0$. Sequentially modified images exhibit high discrepancy.

### Phase 4: Dataset Synthesis & Compilation (`create_samples.py` & `buat_dataset.py`)
1. **Synthetic Carrier Generation (`create_samples.py`):** Generates natural-like images with continuous sinusoidal color gradients and realistic spatial noise distributions.
2. **Class Pairing:** For each clean image (Label `0`), an identical carrier is embedded with a secret payload from a predefined test suite to create the stego sample (Label `1`).
3. **Matrix Compilation (`buat_dataset.py`):** Iterates over `dataset/bersih` and `dataset/stego`, extracts 12-dimensional feature vectors via `utils.py`, and compresses them into `dataset.npz` containing feature matrix $X$ and ground-truth labels $y$.

### Phase 5: Supervised Model Training (`latih_model.py`)
1. **Stratified Partitioning:** Splits dataset into 80% training and 20% testing sets using stratified sampling to preserve class balance.
2. **Dual Model Architecture:**
   - **Decision Tree (`DecisionTreeClassifier`):** Learns non-linear orthogonal decision boundaries based on leading-zero runs and spatial bit-transition discrepancies.
   - **Gaussian Naive Bayes (`GaussianNB`):** Evaluates Gaussian class conditional probabilities across statistical features.
3. **Weight Serialization:** Evaluates accuracy metrics on the hold-out test set and serializes trained models to `model_dt.joblib` and `model_nb.joblib`.

### Phase 6: Autonomous Target Inference (`prediksi.py`)
1. Accepts an arbitrary suspect image path via CLI.
2. Deserializes the trained `.joblib` models.
3. Extracts the 12-dimensional feature vector in real time.
4. Outputs independent classification verdicts from both Decision Tree and Naive Bayes (`Bersih` vs `Tersembunyi`).

### Phase 7: Deterministic Payload Extraction (`stego_engine.py decode`)
1. If an image is flagged as stego, `stego_engine.py decode` reads the first 32 bits from pixel $(0, 0)$.
2. Converts the 32-bit sequence to integer $L$ (payload bit length).
3. Reads exactly $L$ subsequent bits, packs them into 8-bit bytes, and decodes the string back to UTF-8 text without reading leftover carrier noise.

---

## Quickstart & End-to-End Demo

Run the automated demonstration to execute the entire 6-phase pipeline (sample generation $\rightarrow$ feature extraction $\rightarrow$ model training $\rightarrow$ visual attack $\rightarrow$ prediction $\rightarrow$ message extraction) in a single command:

```bash
git clone https://github.com/AditCodeX/Steganalysis.git
cd Steganalysis
pip install -r requirements.txt
python demo.py
```

### Verified Demo Output:
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
--- Melatih Model Decision Tree ---
Akurasi Decision Tree pada data uji: 100.00%
--- Melatih Model Naive Bayes ---
Akurasi Naive Bayes pada data uji: 100.00%

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

## Command Line Usage

### 1. Hide a Secret Message (Encode)
```bash
python stego_engine.py encode -i carrier.png -m "TOP_SECRET: Coordinates 0x7FA4" -o stego_output.png
```

### 2. Extract Hidden Message (Decode)
```bash
python stego_engine.py decode -i stego_output.png
```

### 3. Visual LSB Attack Inspection
```bash
# Save visual analysis plot without opening GUI window
python visualize_lsb.py -i stego_output.png -o visual_report.png --no-show

# Interactive inspection with GUI window
python visualize_lsb.py -i stego_output.png
```

### 4. Machine Learning Training & Inference Workflow

1. **Generate Synthetic Training Samples:**
   ```bash
   python create_samples.py
   ```
2. **Compile Feature Matrix:**
   ```bash
   python buat_dataset.py
   ```
3. **Train Classifiers:**
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
- `Pillow >= 10.0.0`
- `numpy >= 1.24.0`
- `scikit-learn >= 1.3.0`
- `joblib >= 1.3.0`
- `matplotlib >= 3.7.0`
- `scipy >= 1.10.0`

---

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
