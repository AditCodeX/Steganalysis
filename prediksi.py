"""
Automated Target Image Forensic Classifier
Loads serialized Decision Tree & Gaussian Naive Bayes models, extracts 12D spatial
and statistical features from an unseen target image, and outputs a forensic verdict.
"""

import argparse
import json
import sys
from PIL import Image
import joblib
from utils import ekstrak_fitur

def prediksi_gambar(path_gambar, path_model_dt="model_dt.joblib", path_model_nb="model_nb.joblib", as_json=False):
    """Classifies a target image as Clean or Stego using trained models."""
    try:
        model_dt = joblib.load(path_model_dt)
        model_nb = joblib.load(path_model_nb)

        gambar = Image.open(path_gambar)
        fitur_gambar = ekstrak_fitur(gambar)
        fitur_2d = [fitur_gambar]

        pred_dt = int(model_dt.predict(fitur_2d)[0])
        pred_nb = int(model_nb.predict(fitur_2d)[0])

        hasil_dt = "Tersembunyi" if pred_dt == 1 else "Bersih"
        hasil_nb = "Tersembunyi" if pred_nb == 1 else "Bersih"
        verdict = "STEGO (TERSEMBUNYI)" if (pred_dt == 1 or pred_nb == 1) else "CLEAN (BERSIH)"

        if as_json:
            out = {
                "image": path_gambar,
                "decision_tree": hasil_dt,
                "naive_bayes": hasil_nb,
                "verdict": verdict,
                "is_stego": bool(pred_dt == 1 or pred_nb == 1)
            }
            print(json.dumps(out, indent=2))
            return out

        print("\n" + "=" * 50)
        print("         HASIL ANALISIS FORENSIK GAMBAR")
        print("=" * 50)
        print(f"Target Gambar          : {path_gambar}")
        print(f"Prediksi Decision Tree : {hasil_dt}")
        print(f"Prediksi Naive Bayes   : {hasil_nb}")
        print("-" * 50)
        print(f"KESIMPULAN AKHIR       : {verdict}")
        print("=" * 50)

        return verdict

    except FileNotFoundError as e:
        print(f"[-] Error: File tidak ditemukan -> {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[-] Terjadi error saat klasifikasi: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deteksi steganografi pada gambar menggunakan model Machine Learning.")
    parser.add_argument("path_gambar", help="Path ke file gambar yang akan dianalisis.")
    parser.add_argument("--model-dt", default="model_dt.joblib", help="Path file model Decision Tree (default: 'model_dt.joblib').")
    parser.add_argument("--model-nb", default="model_nb.joblib", help="Path file model Naive Bayes (default: 'model_nb.joblib').")
    parser.add_argument("--json", action="store_true", help="Output hasil dalam format JSON.")

    args = parser.parse_args()
    prediksi_gambar(args.path_gambar, path_model_dt=args.model_dt, path_model_nb=args.model_nb, as_json=args.json)
