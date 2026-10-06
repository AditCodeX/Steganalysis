"""
Compatibility wrapper for stego_engine.py
Maintained for backwards compatibility with earlier workflow scripts.
"""

from stego_engine import Steganography

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Alat Steganografi Gambar (Alias for stego_engine.py)")
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
