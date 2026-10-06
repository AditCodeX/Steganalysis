# Steganalysis Toolkit

<div align="center">

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![NumPy](https://img.shields.io/badge/numpy-2.0+-green.svg)](https://numpy.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)
[![Pillow](https://img.shields.io/badge/pillow-10.0+-yellow.svg)](https://python-pillow.org/)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[![Security Focus: Forensics](https://img.shields.io/badge/domain-digital%20forensics-red.svg)](https://github.com/AditCodeX)

**Engine steganografi gambar digital dan suite steganalisis forensik open-source.**  
Mencakup sisi offensive (penyisipan sekuensial LSB dengan framing header 32-bit) dan sisi defensive/forensik (visual bit-plane attack serta klasifikasi Machine Learning otomatis).

<br/>

<!-- System Architecture & Workflow Diagram (Auto-Adapts to Dark / Light GitHub Theme) -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/AditCodeX/Steganalysis/main/assets/architecture_dark.png" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/AditCodeX/Steganalysis/main/assets/architecture_light.png" />
  <img src="https://raw.githubusercontent.com/AditCodeX/Steganalysis/main/assets/architecture_dark.png" alt="Steganalysis Toolkit System Architecture and Data Flow" width="100%" />
</picture>

</div>

---

## 1. Arsitektur Sistem & Kemampuan Modul

| Modul | Peran Pipeline | Fungsi Utama | Teknologi Inti |
| :--- | :--- | :--- | :--- |
| **`stego_engine.py`** | Offensive / Covert Channel | Menyisipkan & mengekstrak payload UTF-8 dengan header panjang 32-bit | Bitwise masking `(Pixel & 0xFE) \| bit` |
| **`visualize_lsb.py`** | Defensive / Visual Forensics | Mengekspos pita noise frekuensi tinggi pada bit-plane LSB | Modulo-2 slicing `(Pixel % 2) * 255` |
| **`utils.py`** | Feature Engineering | Mengekstrak 12 vektor fitur korelasi spasial & statistik | Transisi $\Delta\text{LSB}$ & kerapatan prefix |
| **`buat_dataset.py`** | Dataset Pipeline | Kompilasi batch fitur direktori gambar ke format `dataset.npz` | Batch matrix compilation |
| **`create_samples.py`** | Synthetic Generator | Membuat pasangan dataset sintetis (clean & stego) otomatis | Procedural carrier generator |
| **`latih_model.py`** | Machine Learning | Melatih model classifier untuk membedakan gambar bersih vs stego | Decision Tree & Gaussian Naive Bayes |
| **`prediksi.py`** | Automated Inference | Memindai target gambar dan memberikan hasil analisis forensik | Kueri model terserialisasi `.joblib` |
| **`demo.py`** | Automated Verification | Menjalankan seluruh 6 fase workflow secara end-to-end 1-klik | Full pipeline automation |

---

## 2. Demonstrasi Forensik Visual Attack

Pada steganografi LSB sekuensial, pesan rahasia tidak terlihat oleh mata manusia secara visual ($>58\text{ dB}$ PSNR). Namun, dengan mengisolasi bit-plane LSB ($Bit = \text{Pixel} \pmod 2$) dan diskalakan ke kontras penuh ($0 \rightarrow 0, 1 \rightarrow 255$), data yang disisipkan langsung terlihat jelas sebagai pita noise berdensitas tinggi:

<div align="center">
  <img src="https://raw.githubusercontent.com/AditCodeX/Steganalysis/main/assets/visual_attack_comparison.png" alt="LSB Bit-Plane Visual Attack Diagnostic Comparison" width="100%" />
</div>

---

## 3. Aturan Format & Kalkulasi Kapasitas

### A. Format Gambar yang Didukung vs Dilarang
Steganografi berbasis LSB memodifikasi bit biner terkecil dari nilai piksel mentah. Oleh karena itu, terdapat aturan ketat terkait format berkas:

* **Format yang Didukung (Lossless):** **`.png`**, **`.bmp`**, **`.tiff`**.  
  *Format ini mempertahankan nilai bit piksel secara eksak tanpa kompresi destruktif.*
* **Format yang DILARANG (Lossy):** **`.jpg`**, **`.jpeg`**, **`.webp`**.  
  *Kompresi Discrete Cosine Transform (DCT) dan kuantisasi JPEG akan mengacak dan menghancurkan bit LSB, sehingga pesan rahasia tidak dapat didecode.*

### B. Rumus Kalkulasi Kapasitas Maksimal
Untuk gambar RGB dengan dimensi Lebar ($W$) dan Tinggi ($H$), setiap piksel memiliki 3 channel (Red, Green, Blue). Total bit kapasitas dikurangi 32-bit untuk header panjang:

$$\text{Kapasitas Maksimal (Karakter/Byte)} = \left\lfloor \frac{W \times H \times 3 - 32}{8} \right\rfloor$$

| Resolusi Gambar | Total Bit Tersedia | Estimasi Kapasitas Teks |
| :--- | :--- | :--- |
| **$128 \times 128\text{ px}$** | $49.152\text{ bit}$ | **$\approx 6.140\text{ karakter}$** ($\approx 6\text{ KB}$) |
| **$256 \times 256\text{ px}$** | $196.608\text{ bit}$ | **$\approx 24.572\text{ karakter}$** ($\approx 24\text{ KB}$) |
| **$512 \times 512\text{ px}$** | $786.432\text{ bit}$ | **$\approx 98.300\text{ karakter}$** ($\approx 98\text{ KB}$) |
| **$1920 \times 1080\text{ px}$ (FHD)** | $6.220.800\text{ bit}$ | **$\approx 777.596\text{ karakter}$** ($\approx 777\text{ KB}$) |

---

## 4. Cara Kerja Teknis

### A. Framing 32-Bit Length Prefix
Steganografi konvensional umumnya mengandalkan karakter delimiter (seperti `\0` atau `EOF`), yang rentan memicu terminasi dini jika payload memuat biner nol. Engine ini menyisipkan **32-bit fixed-width binary header** ($L$ bit) di awal payload, memastikan proses recovery data berjalan deterministik dan bebas korupsi:

```text
Bitstream = [32-Bit Header (Length L)] + [UTF-8 Payload (L Bits)]
```

### B. 12 Indikator Fitur Forensik

Deteksi otomatis memanfaatkan 12 indikator numerik untuk membedakan korelasi alami gambar dari anomali modifikasi steganografi:

| Indeks Fitur | Nama Indikator | Mekanisme & Signifikansi Forensik | Nilai Ekspektasi Baseline |
| :--- | :--- | :--- | :--- |
| **F1 – F2** | **Header Bit Densities** | Rata-rata densitas bit pada 32 dan 256 piksel pertama | Klaster leading zeros vs ~0.50 pada gambar alami |
| **F3** | **Leading Zero Run** | Jumlah bit 0 berurutan mulai dari bit 0 | 15–25 nol menandakan prefix panjang data 32-bit |
| **F4 – F9** | **RGB Channel Moments** | Rata-rata global dan standar deviasi per channel (R, G, B) | Mendeteksi pergeseran paritas LSB antar channel warna |
| **F10 – F11** | **Spatial ΔLSB Transitions** | Frekuensi flip bit antar piksel tetangga horizontal & vertikal | Bit acak stego mendekati laju transisi ~0.50 |
| **F12** | **Local Discrepancy Metric** | Selisih laju transisi blok head modifikasi vs blok tail asli (`\|Rate_head - Rate_tail\|`) | ~0 pada foto alami; meningkat drastis pada carrier stego |

---

## 5. Panduan Lengkap Penggunaan CLI

### A. Instalasi Dependensi
```bash
# 1. Clone repositori
git clone https://github.com/AditCodeX/Steganalysis.git
cd Steganalysis

# 2. Buat virtual environment
python -m venv .venv
source .venv/bin/activate  # Di Windows: .venv\Scripts\activate

# 3. Pasang paket pustaka
pip install -r requirements.txt
```

---

### B. Operasi Steganografi (Encode & Decode)

#### 1. Menyisipkan Pesan String Langsung (`-m`)
```bash
python stego_engine.py encode -i carrier.png -m "TOP_SECRET: Koordinat 0x7FA4" -o stego_output.png
```
**Output Terminal:**
```text
[+] Message encoded successfully (29 chars / 232 payload bits) -> stego_output.png
```

#### 2. Menyisipkan Pesan dari File Teks (`-f`)
Cocok untuk menyembunyikan payload dokumen, source code, atau sertifikat rahasia:
```bash
python stego_engine.py encode -i carrier.png -f secret_payload.txt -o stego_output.png
```

#### 3. Mengekstrak Pesan Rahasia (Decode)
Membaca pesan ke layar console secara langsung:
```bash
python stego_engine.py decode -i stego_output.png
```
**Output Terminal:**
```text
[+] Decoded message (29 chars):
    "TOP_SECRET: Koordinat 0x7FA4"
```

#### 4. Mengekstrak dan Menyimpan ke File Teks (`-o`)
```bash
python stego_engine.py decode -i stego_output.png -o hasil_ekstraksi.txt
```
**Output Terminal:**
```text
[+] Decoded message (29 chars):
    "TOP_SECRET: Koordinat 0x7FA4"
[+] Extracted message saved to file: hasil_ekstraksi.txt
```

---

### C. Inspeksi Forensik Visual Bit-Plane (`visualize_lsb.py`)

#### 1. Mode Headless (Simpan Laporan Gambar Tanpa Membuka Jendela GUI)
Cocok untuk server Linux, terminal SSH, atau automated pipeline:
```bash
python visualize_lsb.py -i stego_output.png -o visual_report.png --no-show
```
**Output Terminal:**
```text
[+] LSB visual analysis saved to: visual_report.png
```

#### 2. Mode Interaktif (Membuka Jendela Grafik GUI Matplotlib)
```bash
python visualize_lsb.py -i stego_output.png
```

---

### D. Pipeline Forensik Machine Learning

#### Langkah 1: Generate Pasangan Sampel Dataset Sintetis
Menghasilkan gambar bersih (`clean_*.png`) dan gambar stego (`stego_*.png`) bergradien halus:
```bash
# Membuat 30 pasang sampel (total 60 gambar) ke direktori 'dataset'
python create_samples.py -n 30 -o dataset
```
**Output Terminal:**
```text
[*] Generating 30 clean and 30 stego samples in 'dataset'...
[+] Message encoded successfully (72 chars / 576 payload bits) -> dataset/stego/stego_000.png
...
[+] Successfully created sample dataset in 'dataset/'.
```

#### Langkah 2: Ekstraksi 12 Fitur Forensik ke Format `.npz`
```bash
python buat_dataset.py --bersih dataset/bersih --stego dataset/stego -o dataset.npz
```
**Output Terminal:**
```text
[*] Memproses folder 'dataset/bersih' (label 0)...
[+] Berhasil mengekstrak 30 gambar dari 'dataset/bersih'.
[*] Memproses folder 'dataset/stego' (label 1)...
[+] Berhasil mengekstrak 30 gambar dari 'dataset/stego'.

[+] Dataset berhasil dibuat dari 60 sampel -> dataset.npz
```

#### Langkah 3: Melatih Model Decision Tree & Gaussian Naive Bayes
```bash
python latih_model.py -d dataset.npz --output-dt model_dt.joblib --output-nb model_nb.joblib --test-size 0.2
```
**Output Terminal:**
```text
[*] Memuat dataset dari 'dataset.npz'...
[+] Dataset dimuat: Total 60 sampel (48 train, 12 test).

--- Melatih Model Decision Tree ---
Akurasi Decision Tree pada data uji: 100.00%
[+] Model Decision Tree disimpan di: model_dt.joblib

--- Melatih Model Naive Bayes ---
Akurasi Naive Bayes pada data uji: 100.00%
[+] Model Naive Bayes disimpan di: model_nb.joblib
```

#### Langkah 4: Prediksi Gambar Sasaran yang Mencurigakan

##### Mode Teks Standar:
```bash
python prediksi.py bukti_gambar.png
```
**Output Terminal:**
```text
==================================================
         HASIL ANALISIS FORENSIK GAMBAR
==================================================
Target Gambar          : bukti_gambar.png
Prediksi Decision Tree : Tersembunyi
Prediksi Naive Bayes   : Tersembunyi
--------------------------------------------------
KESIMPULAN AKHIR       : STEGO (TERSEMBUNYI)
==================================================
```

##### Mode JSON Output (`--json`):
Sangat berguna untuk integrasi automated triage / SIEM / pipeline API:
```bash
python prediksi.py bukti_gambar.png --json
```
**Output Terminal:**
```json
{
  "image": "bukti_gambar.png",
  "decision_tree": "Tersembunyi",
  "naive_bayes": "Tersembunyi",
  "verdict": "STEGO (TERSEMBUNYI)",
  "is_stego": true
}
```

---

### E. Verifikasi Otomatis 1-Klik (`demo.py`)
Mengeksekusi seluruh siklus hidup proyek secara terintegrasi (generate data $\rightarrow$ ekstraksi fitur $\rightarrow$ pelatihan model $\rightarrow$ visual attack $\rightarrow$ prediksi $\rightarrow$ ekstraksi pesan):
```bash
python demo.py
```
**Output Terminal Terverifikasi:**
```text
=================================================================
  STEGANALYSIS TOOLKIT - END-TO-END DEMO
=================================================================

[Phase 1] Generating Synthetic Dataset...
[*] Generating 15 clean and 15 stego samples in 'dataset_demo'...
[+] Successfully created sample dataset in 'dataset_demo/'.

[Phase 2] Compiling Dataset Features...
[+] Dataset berhasil dibuat dari 30 sampel -> dataset_demo.npz

[Phase 3] Training Classifiers...
Akurasi Decision Tree pada data uji: 100.00%
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

## 6. Tabel Referensi Argumen CLI

| Skrip CLI | Argumen / Flag | Tipe | Default | Keterangan |
| :--- | :--- | :--- | :--- | :--- |
| **`stego_engine.py encode`** | `-i, --input` | Wajib | - | Path gambar input lossless (PNG/BMP/TIFF) |
| | `-m, --message` | Pilihan | - | Pesan teks string yang akan disembunyikan |
| | `-f, --file` | Pilihan | - | Path file teks berisi pesan rahasia |
| | `-o, --output` | Wajib | - | Path berkas gambar stego output |
| **`stego_engine.py decode`** | `-i, --input` | Wajib | - | Path gambar stego yang akan diekstrak |
| | `-o, --output` | Opsional | None | Path file teks untuk menyimpan hasil dekode |
| **`visualize_lsb.py`** | `-i, --input` | Wajib | - | Path gambar yang akan diinspeksi bit-plane-nya |
| | `-o, --output` | Opsional | None | Path berkas gambar untuk menyimpan plot grafik |
| | `--no-show` | Flag | False | Menonaktifkan jendela pop-up GUI Matplotlib |
| **`create_samples.py`** | `-n, --num-samples` | Opsional | `20` | Jumlah pasang sampel per kelas (bersih & stego) |
| | `-o, --output` | Opsional | `'dataset'` | Direktori output penyimpanan gambar |
| **`buat_dataset.py`** | `--bersih` | Opsional | `'dataset/bersih'` | Direktori berkas gambar kelas bersih |
| | `--stego` | Opsional | `'dataset/stego'` | Direktori berkas gambar kelas stego |
| | `-o, --output` | Opsional | `'dataset.npz'` | Berkas output biner terkompresi NumPy |
| **`latih_model.py`** | `-d, --dataset` | Opsional | `'dataset.npz'` | Berkas dataset input fitur |
| | `--output-dt` | Opsional | `'model_dt.joblib'` | Path output model serial Decision Tree |
| | `--output-nb` | Opsional | `'model_nb.joblib'` | Path output model serial Gaussian Naive Bayes |
| | `--test-size` | Opsional | `0.2` | Rasio pembagian data uji (20%) |
| **`prediksi.py`** | `path_gambar` | Positional | - | Berkas gambar sasaran yang akan diuji |
| | `--model-dt` | Opsional | `'model_dt.joblib'` | Lokasi berkas model Decision Tree |
| | `--model-nb` | Opsional | `'model_nb.joblib'` | Lokasi berkas model Naive Bayes |
| | `--json` | Flag | False | Menampilkan output terstruktur format JSON |

---

## 7. Panduan Troubleshooting & FAQ

#### Q: Mengapa proses ekstraksi pesan gagal atau menghasilkan teks acak/rusak?
* **Penyebab:** Gambar stego disimpan dalam format kompresi lossy (`.jpg`, `.jpeg`, `.webp`), atau diedit/di-resize oleh aplikasi pengolah gambar pihak ketiga. Kompresi lossy mengubah nilai piksel dan menghancurkan bit LSB.
* **Solusi:** Selalu gunakan format lossless (`.png` atau `.bmp`) dan hindari kompresi ulang gambar setelah pesan disisipkan.

#### Q: Muncul error `Payload exceeds carrier capacity`?
* **Penyebab:** Ukuran teks pesan (dalam bit) melebihi kapasitas total bit piksel gambar.
* **Solusi:** Gunakan gambar pembawa dengan dimensi resolusi yang lebih besar (lihat tabel kalkulasi pada Bab 3), atau kurangi panjang pesan yang disisipkan.

#### Q: Error `FileNotFoundError: model_dt.joblib` saat menjalankan `prediksi.py`?
* **Penyebab:** Model Machine Learning belum dilatih pada environment lokal Anda.
* **Solusi:** Jalankan `python demo.py` atau `python latih_model.py` terlebih dahulu untuk menghasilkan bobot model terkompilasi `.joblib`.

---

## 8. Struktur Repositori

```
Steganalysis/
├── assets/
│   ├── architecture_dark.png        # Diagram arsitektur sistem (Dark theme)
│   ├── architecture_light.png       # Diagram arsitektur sistem (Light theme)
│   └── visual_attack_comparison.png # Perbandingan visual attack side-by-side
├── stego_engine.py                  # LSB encoder & decoder dengan framing header 32-bit
├── visualize_lsb.py                 # Ekstraktor visual bit-plane & tool plot visual attack
├── utils.py                         # Ekstraktor 12 fitur korelasi spasial & statistik
├── buat_dataset.py                  # Kompiler dataset dari direktori gambar ke dataset.npz
├── create_samples.py                # Generator dataset sintetis untuk pengujian
├── latih_model.py                   # Trainer model Decision Tree & Gaussian Naive Bayes
├── prediksi.py                      # CLI inference untuk analisis gambar target (Text & JSON)
├── demo.py                          # Skrip verifikasi end-to-end otomatis
├── requirements.txt                 # Dependensi pustaka Python
└── LICENSE                          # GNU General Public License v3.0
```

---

## 9. Pengembang & Lisensi

Dikembangkan oleh **[AditCodeX](https://github.com/AditCodeX)**.  
Dilisensikan di bawah **[GNU General Public License v3.0](LICENSE)**.
