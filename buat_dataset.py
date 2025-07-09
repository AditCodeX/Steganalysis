# buat_dataset.py (Versi Diperbarui)

import os
import numpy as np
from PIL import Image
from utils import ekstrak_fitur # Impor fungsi dari utils.py

def proses_folder(folder_path, label, fitur, daftar_label):
    """Fungsi pembantu untuk memproses satu folder gambar."""
    print(f"Memproses folder '{folder_path}' dengan label '{label}'...")
    for nama_file in os.listdir(folder_path):
        if nama_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            path_file = os.path.join(folder_path, nama_file)
            try:
                gambar = Image.open(path_file)
                fitur.append(ekstrak_fitur(gambar))
                daftar_label.append(label)
                # print(f"  - Memproses {nama_file}... OK") # Uncomment jika ingin log per file
            except Exception as e:
                print(f"Gagal memproses {nama_file}: {e}")

def buat_dan_simpan_dataset(folder_bersih, folder_stego, file_output):
    """
    Membuat dataset fitur dan label dari dua folder terpisah
    (bersih dan stego), lalu menyimpannya ke file.
    """
    fitur = []
    label = []
    
    # Proses folder gambar bersih (label 0)
    proses_folder(folder_bersih, 0, fitur, label)
    
    # Proses folder gambar stego (label 1)
    proses_folder(folder_stego, 1, fitur, label)
    
    # Periksa apakah dataset berhasil dibuat
    if not fitur:
        print("\nTidak ada gambar yang berhasil diproses. Periksa path folder dan isi folder Anda.")
        return

    # Simpan dataset ke file .npz (format terkompresi NumPy)
    np.savez(file_output, X=np.array(fitur), y=np.array(label))
    print(f"\nDataset berhasil dibuat dari {len(fitur)} gambar dan disimpan di: {file_output}")

if __name__ == "__main__":
    # Path ke folder-folder dataset Anda
    folder_path_bersih = "dataset/bersih"
    folder_path_stego = "dataset/stego"
    
    # Nama file output untuk dataset yang sudah diproses
    file_dataset_output = "dataset.npz"
    
    buat_dan_simpan_dataset(folder_path_bersih, folder_path_stego, file_dataset_output)