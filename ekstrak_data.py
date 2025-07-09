# steganography_tool.py (Versi Panjang Data)

import argparse
from PIL import Image
import numpy as np

class Steganography:
    """
    Versi Steganography yang menggunakan prefix panjang data untuk hasil yang akurat.
    """
    def _tulis_data_ke_piksel(self, array_piksel, data_biner):
        """Fungsi pembantu untuk menulis data biner ke array piksel."""
        indeks_data = 0
        panjang_data = len(data_biner)
        tinggi, lebar, _ = array_piksel.shape

        for y in range(tinggi):
            for x in range(lebar):
                for c in range(3):
                    if indeks_data < panjang_data:
                        nilai_piksel = array_piksel[y, x, c]
                        bit_data = int(data_biner[indeks_data])
                        array_piksel[y, x, c] = (nilai_piksel & 0b11111110) | bit_data
                        indeks_data += 1
                    else:
                        return array_piksel
        return array_piksel

    def encode(self, path_gambar_input, pesan, path_gambar_output):
        """
        Menyembunyikan pesan dengan didahului oleh panjang pesannya.
        """
        try:
            gambar = Image.open(path_gambar_input).convert('RGB')
            array_piksel = np.array(gambar)

            pesan_biner = ''.join(format(ord(i), '08b') for i in pesan)
            panjang_pesan_dalam_bit = len(pesan_biner)
            
            # Buat header 32-bit yang berisi panjang pesan
            header_panjang = format(panjang_pesan_dalam_bit, '032b')
            
            data_lengkap_biner = header_panjang + pesan_biner

            kapasitas_gambar = array_piksel.size
            if len(data_lengkap_biner) > kapasitas_gambar:
                print("Error: Pesan terlalu panjang untuk gambar ini.")
                return False
            
            array_piksel_modifikasi = self._tulis_data_ke_piksel(array_piksel, data_lengkap_biner)
            
            gambar_stego = Image.fromarray(array_piksel_modifikasi)
            gambar_stego.save(path_gambar_output)
            print(f"Pesan berhasil disembunyikan dan disimpan di: {path_gambar_output}")
            return True

        except Exception as e:
            print(f"Terjadi error saat encoding: {e}")
            return False

    def decode(self, path_gambar_stego):
        """
        Mengekstrak pesan dengan membaca header panjang terlebih dahulu.
        """
        try:
            gambar = Image.open(path_gambar_stego).convert('RGB')
            array_piksel = np.array(gambar)
            
            bit_terekstrak = ""
            # Ekstrak 32 bit pertama untuk mendapatkan header panjang
            for y in range(array_piksel.shape[0]):
                for x in range(array_piksel.shape[1]):
                    for c in range(3):
                        bit_terekstrak += str(array_piksel[y, x, c] % 2)
                        if len(bit_terekstrak) == 32:
                            break
                    if len(bit_terekstrak) == 32: break
                if len(bit_terekstrak) == 32: break
            
            panjang_pesan_dalam_bit = int(bit_terekstrak, 2)
            
            # Ekstrak sisa pesan sesuai panjang yang didapat
            bit_terekstrak = ""
            total_bit_untuk_dibaca = 32 + panjang_pesan_dalam_bit
            bit_dibaca = 0

            for y in range(array_piksel.shape[0]):
                for x in range(array_piksel.shape[1]):
                    for c in range(3):
                        if bit_dibaca < total_bit_untuk_dibaca:
                            bit_terekstrak += str(array_piksel[y, x, c] % 2)
                            bit_dibaca += 1
                        else:
                            break
                    if bit_dibaca >= total_bit_untuk_dibaca: break
                if bit_dibaca >= total_bit_untuk_dibaca: break
            
            # Ambil hanya bagian pesan (setelah 32 bit header)
            pesan_biner = bit_terekstrak[32:]
            
            pesan_ditemukan = ""
            for i in range(0, len(pesan_biner), 8):
                byte = pesan_biner[i:i+8]
                if len(byte) == 8:
                    pesan_ditemukan += chr(int(byte, 2))
            
            print("\n--- Pesan Ditemukan (Metode Panjang Data) ---")
            print(pesan_ditemukan)
            return pesan_ditemukan

        except Exception as e:
            print(f"Terjadi error saat decoding: {e}")
            return None

# --- Antarmuka Command Line (Tidak ada perubahan) ---
if __name__ == "__main__":
    # Bagian ini sama persis seperti Opsi 1
    parser = argparse.ArgumentParser(description="Alat Steganografi Gambar")
    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_encode = subparsers.add_parser("encode", help="Sembunyikan pesan dalam gambar.")
    parser_encode.add_argument("-i", "--input", required=True, help="Path gambar input (bersih).")
    parser_encode.add_argument("-m", "--message", required=True, help="Pesan teks yang akan disembunyikan.")
    parser_encode.add_argument("-o", "--output", required=True, help="Path untuk menyimpan gambar output (stego).")
    parser_decode = subparsers.add_parser("decode", help="Ekstrak pesan dari gambar.")
    parser_decode.add_argument("-i", "--input", required=True, help="Path gambar stego yang akan di-decode.")
    args = parser.parse_args()
    tool = Steganography()
    if args.command == "encode":
        tool.encode(args.input, args.message, args.output)
    elif args.command == "decode":
        tool.decode(args.input)