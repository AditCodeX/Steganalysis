# Steganalysis Toolkit

<div align="center">

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![NumPy](https://img.shields.io/badge/numpy-2.0+-green.svg)](https://numpy.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)
[![Pillow](https://img.shields.io/badge/pillow-10.0+-yellow.svg)](https://python-pillow.org/)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[![Security Focus: Forensics](https://img.shields.io/badge/domain-digital%20forensics-red.svg)](https://github.com/AditCodeX)

**Engine steganografi gambar digital dan suite steganalisis forensik open-source.**  
Mencakup sisi offensive (penyisipan sekuensial LSB) dan sisi defensive/forensik (visual bit-plane attack serta klasifikasi Machine Learning).

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
| **`latih_model.py`** | Machine Learning | Melatih model classifier untuk membedakan gambar bersih vs stego | Decision Tree & Gaussian Naive Bayes |
| **`prediksi.py`** | Automated Inference | Memindai target gambar dan memberikan hasil analisis forensik | Kueri model terserialisasi `.joblib` |

---

## 2. Demonstrasi Forensik Visual Attack

Pada steganografi LSB sekuensial, pesan rahasia tidak terlihat oleh mata manusia secara visual ($>58\text{ dB}$ PSNR). Namun, dengan mengisolasi bit-plane LSB ($Bit = \text{Pixel} \pmod 2$) dan diskalakan ke kontras penuh ($0 \rightarrow 0, 1 \rightarrow 255$), data yang disisipkan langsung terlihat jelas sebagai pita noise berdensitas tinggi:

<div align="center">
  <img src="https://raw.githubusercontent.com/AditCodeX/Steganalysis/main/assets/visual_attack_comparison.png" alt="LSB Bit-Plane Visual Attack Diagnostic Comparison" width="100%" />
</div>

---

## 3. Cara Kerja Teknis

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

## 4. Panduan Penggunaan & CLI

### Instalasi Lingkungan
```bash
git clone https://github.com/AditCodeX/Steganalysis.git
cd Steganalysis
python -m venv .venv
source .venv/bin/activate  # Di Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1. Menyembunyikan & Mengekstrak Pesan Rahasia
```bash
# Sembunyikan pesan ke dalam gambar
python stego_engine.py encode -i carrier.png -m "TOP_SECRET: Coordinates 0x7FA4" -o stego.png

# Ekstrak pesan dari gambar stego
python stego_engine.py decode -i stego.png
```

### 2. Inspeksi Visual Bit-Plane LSB
```bash
# Buat laporan grafik visual attack (disimpan ke file)
python visualize_lsb.py -i stego.png -o visual_report.png --no-show
```

### 3. Pipeline Forensik Machine Learning
```bash
# 1. Generate sampel dataset sintetis (bersih & stego)
python create_samples.py

# 2. Ekstrak 12 fitur dan kompilasi ke dataset.npz
python buat_dataset.py

# 3. Latih model Decision Tree & Naive Bayes
python latih_model.py

# 4. Prediksi gambar target yang mencurigakan
python prediksi.py target_image.png
```

### 4. Verifikasi Otomatis Sekali Jalan
```bash
python demo.py
```

*Mengeksekusi seluruh 6 fase pipeline secara end-to-end, mengevaluasi akurasi data uji (100.0%), dan memverifikasi rekonstruksi payload secara utuh.*

---

## 5. Struktur Repositori

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
├── prediksi.py                      # CLI inference untuk analisis gambar target
├── demo.py                          # Skrip verifikasi end-to-end otomatis
├── requirements.txt                 # Dependensi pustaka Python
└── LICENSE                          # GNU General Public License v3.0
```

---

## 6. Pengembang & Lisensi

Dikembangkan oleh **[AditCodeX](https://github.com/AditCodeX)**.  
Dilisensikan di bawah **[GNU General Public License v3.0](LICENSE)**.
