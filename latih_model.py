"""
Machine Learning Model Training Module
Loads .npz feature matrix, trains Decision Tree & Gaussian Naive Bayes classifiers,
evaluates accuracy metrics, and serializes trained models via joblib.
"""

import argparse
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report
import joblib

def latih_dan_simpan_model(file_dataset, path_output_dt, path_output_nb, test_size=0.2):
    """Loads dataset, trains classifiers, and serializes models to disk."""
    print(f"[*] Memuat dataset dari '{file_dataset}'...")
    data = np.load(file_dataset)
    X, y = data['X'], data['y']

    X_latih, X_uji, y_latih, y_uji = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    print(f"[+] Dataset dimuat: Total {len(X)} sampel ({len(X_latih)} train, {len(X_uji)} test).")

    # --- Model 1: Decision Tree ---
    print("\n--- Melatih Model Decision Tree ---")
    dt_model = DecisionTreeClassifier(random_state=42)
    dt_model.fit(X_latih, y_latih)
    akurasi_dt = accuracy_score(y_uji, dt_model.predict(X_uji))
    print(f"Akurasi Decision Tree pada data uji: {akurasi_dt * 100:.2f}%")
    joblib.dump(dt_model, path_output_dt)
    print(f"[+] Model Decision Tree disimpan di: {path_output_dt}")

    # --- Model 2: Gaussian Naive Bayes ---
    print("\n--- Melatih Model Naive Bayes ---")
    nb_model = GaussianNB()
    nb_model.fit(X_latih, y_latih)
    akurasi_nb = accuracy_score(y_uji, nb_model.predict(X_uji))
    print(f"Akurasi Naive Bayes pada data uji: {akurasi_nb * 100:.2f}%")
    joblib.dump(nb_model, path_output_nb)
    print(f"[+] Model Naive Bayes disimpan di: {path_output_nb}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Decision Tree and Gaussian Naive Bayes steganalysis classifiers.")
    parser.add_argument("-d", "--dataset", default="dataset.npz", help="Path file input dataset .npz (default: 'dataset.npz').")
    parser.add_argument("--output-dt", default="model_dt.joblib", help="Output path model Decision Tree (default: 'model_dt.joblib').")
    parser.add_argument("--output-nb", default="model_nb.joblib", help="Output path model Naive Bayes (default: 'model_nb.joblib').")
    parser.add_argument("--test-size", type=float, default=0.2, help="Rasio data uji (default: 0.2 / 20%).")
    args = parser.parse_args()

    latih_dan_simpan_model(args.dataset, args.output_dt, args.output_nb, test_size=args.test_size)
