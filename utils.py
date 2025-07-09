# utils.py

import numpy as np
from PIL import Image

def ekstrak_fitur(gambar):
    """
    Menghitung fitur statistik (mean & std dev) dari LSB plane sebuah gambar.
    
    Args:
        gambar (PIL.Image.Image): Objek gambar dari Pillow.

    Returns:
        list: Sebuah list berisi [mean, std_dev] dari LSB plane.
    """
    # Pastikan gambar dalam mode RGB untuk konsistensi
    array_piksel = np.array(gambar.convert('RGB'))
    
    # Ekstrak LSB plane (nilai 0 atau 1)
    lsb_plane = array_piksel % 2
    
    # Hitung fitur statistik
    mean = lsb_plane.mean()
    std_dev = lsb_plane.std()
    
    return [mean, std_dev]