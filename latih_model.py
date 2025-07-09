# latih_model.py

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
import joblib # Untuk menyimpan dan memuat model

def latih_dan_simpan_model(file_dataset, path_output_dt, path_output_nb):
    """Memuat dataset, melatih model, dan menyimpannya."""
    # Muat dataset dari file .npz
    data = np.load(file_dataset)
    X, y = data['X'], data['y']
    
    # Bagi data menjadi data latih dan data uji
    X_latih, X_uji, y_latih, y_uji = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Dataset dimuat. Total sampel: {len(X)}. Melatih dengan {len(X_latih)} sampel.")
    
    # --- Model 1: Decision Tree ---
    print("\n--- Melatih Model Decision Tree ---")
    dt_model = DecisionTreeClassifier(random_state=42)
    dt_model.fit(X_latih, y_latih)
    akurasi_dt = accuracy_score(y_uji, dt_model.predict(X_uji))
    print(f"Akurasi Decision Tree pada data uji: {akurasi_dt * 100:.2f}%")
    # Simpan model ke file
    joblib.dump(dt_model, path_output_dt)
    print(f"Model Decision Tree disimpan di: {path_output_dt}")

    # --- Model 2: Naive Bayes ---
    print("\n--- Melatih Model Naive Bayes ---")
    nb_model = GaussianNB()
    nb_model.fit(X_latih, y_latih)
    akurasi_nb = accuracy_score(y_uji, nb_model.predict(X_uji))
    print(f"Akurasi Naive Bayes pada data uji: {akurasi_nb * 100:.2f}%")
    # Simpan model ke file
    joblib.dump(nb_model, path_output_nb)
    print(f"Model Naive Bayes disimpan di: {path_output_nb}")

if __name__ == "__main__":
    file_dataset_input = "dataset.npz"
    path_dt = "model_dt.joblib"
    path_nb = "model_nb.joblib"
    latih_dan_simpan_model(file_dataset_input, path_dt, path_nb)