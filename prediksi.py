# prediksi.py

import argparse
from PIL import Image
import joblib
from utils import ekstrak_fitur # Impor fungsi dari utils.py

def prediksi_gambar(path_gambar, path_model_dt, path_model_nb):
    """Memuat model dan memprediksi satu gambar."""
    try:
        # Muat model yang sudah dilatih
        model_dt = joblib.load(path_model_dt)
        model_nb = joblib.load(path_model_nb)
        
        # Buka dan proses gambar
        gambar = Image.open(path_gambar)
        fitur_gambar = ekstrak_fitur(gambar)
        
        # Scikit-learn butuh input 2D, jadi kita ubah bentuknya
        fitur_2d = [fitur_gambar]
        
        # Lakukan prediksi
        prediksi_dt = model_dt.predict(fitur_2d)
        prediksi_nb = model_nb.predict(fitur_2d)

        # Terjemahkan hasil (0=Bersih, 1=Tersembunyi)
        hasil_dt = "Tersembunyi" if prediksi_dt[0] == 1 else "Bersih"
        hasil_nb = "Tersembunyi" if prediksi_nb[0] == 1 else "Bersih"
        
        print("\n--- Hasil Prediksi ---")
        print(f"Gambar: {path_gambar}")
        print(f"Prediksi Decision Tree: Gambar ini kemungkinan besar '{hasil_dt}'")
        print(f"Prediksi Naive Bayes:   Gambar ini kemungkinan besar '{hasil_nb}'")
        
    except FileNotFoundError:
        print(f"Error: File tidak ditemukan di '{path_gambar}' atau file model tidak ditemukan.")
    except Exception as e:
        print(f"Terjadi error: {e}")

if __name__ == "__main__":
    # Menggunakan argparse untuk menerima input dari command line
    parser = argparse.ArgumentParser(description="Deteksi steganografi pada sebuah gambar.")
    parser.add_argument("path_gambar", help="Path lengkap ke file gambar yang akan dianalisis.")
    
    args = parser.parse_args()
    
    # Path ke model yang sudah disimpan
    path_model_dt = "model_dt.joblib"
    path_model_nb = "model_nb.joblib"
    
    prediksi_gambar(args.path_gambar, path_model_dt, path_model_nb)