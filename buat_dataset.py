"""
Dataset Compilation Module
Processes clean (label 0) and stego (label 1) image directories, extracts 12D statistical
features via utils.py, and compiles them into a compressed NumPy dataset (.npz).
"""

import os
import argparse
import numpy as np
from PIL import Image
from utils import ekstrak_fitur

def proses_folder(folder_path, label, fitur, daftar_label):
    """Processes all images in a folder and extracts feature vectors."""
    print(f"[*] Memproses folder '{folder_path}' (label {label})...")
    if not os.path.exists(folder_path):
        print(f"[-] Error: Folder tidak ditemukan di '{folder_path}'")
        return

    count = 0
    for nama_file in os.listdir(folder_path):
        if nama_file.lower().endswith(('.png', '.bmp', '.tiff')):
            path_file = os.path.join(folder_path, nama_file)
            try:
                gambar = Image.open(path_file)
                fitur.append(ekstrak_fitur(gambar))
                daftar_label.append(label)
                count += 1
            except Exception as e:
                print(f"[-] Gagal memproses {nama_file}: {e}")
    print(f"[+] Berhasil mengekstrak {count} gambar dari '{folder_path}'.")

def buat_dan_simpan_dataset(folder_bersih, folder_stego, file_output):
    """Compiles clean and stego image feature sets and saves to .npz."""
    fitur = []
    label = []

    proses_folder(folder_bersih, 0, fitur, label)
    proses_folder(folder_stego, 1, fitur, label)

    if not fitur:
        print("\n[-] Error: Tidak ada gambar yang berhasil diproses. Periksa folder dataset Anda.")
        return False

    np.savez(file_output, X=np.array(fitur), y=np.array(label))
    print(f"\n[+] Dataset berhasil dibuat dari {len(fitur)} sampel -> {file_output}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract 12D features and compile clean/stego datasets to .npz.")
    parser.add_argument("--bersih", default="dataset/bersih", help="Path ke direktori gambar bersih (default: 'dataset/bersih').")
    parser.add_argument("--stego", default="dataset/stego", help="Path ke direktori gambar stego (default: 'dataset/stego').")
    parser.add_argument("-o", "--output", default="dataset.npz", help="Path output file .npz (default: 'dataset.npz').")
    args = parser.parse_args()

    buat_dan_simpan_dataset(args.bersih, args.stego, args.output)
