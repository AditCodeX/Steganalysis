"""
LSB Steganography Engine (Inject & Extract)
Embeds and retrieves secret payloads using Least Significant Bit (LSB) encoding
with a 32-bit length header for deterministic, error-free extraction.
"""

import argparse
import sys
import os
import numpy as np
from PIL import Image

class Steganography:
    """
    Sequential LSB Encoder & Decoder using a 32-bit payload length prefix.
    """
    def _write_bits_to_pixels(self, pixel_array: np.ndarray, binary_data: str) -> np.ndarray:
        data_idx = 0
        total_bits = len(binary_data)
        height, width, _ = pixel_array.shape

        for y in range(height):
            for x in range(width):
                for c in range(3):
                    if data_idx < total_bits:
                        pixel_val = pixel_array[y, x, c]
                        bit = int(binary_data[data_idx])
                        pixel_array[y, x, c] = (pixel_val & 0b11111110) | bit
                        data_idx += 1
                    else:
                        return pixel_array
        return pixel_array

    def encode(self, input_image: str, message: str, output_image: str) -> bool:
        """
        Embeds a secret string message into an image.
        """
        try:
            img = Image.open(input_image).convert('RGB')
            arr = np.array(img, dtype=np.uint8)

            msg_bytes = message.encode('utf-8')
            msg_bits = ''.join(format(b, '08b') for b in msg_bytes)
            length_header = format(len(msg_bits), '032b')
            full_payload = length_header + msg_bits

            max_capacity = arr.size
            if len(full_payload) > max_capacity:
                print(f"[-] Error: Payload ({len(full_payload)} bits) exceeds carrier capacity ({max_capacity} bits).", file=sys.stderr)
                return False

            modified_arr = self._write_bits_to_pixels(arr, full_payload)
            stego_img = Image.fromarray(modified_arr)
            stego_img.save(output_image)
            print(f"[+] Message encoded successfully ({len(message)} chars / {len(msg_bits)} payload bits) -> {output_image}")
            return True
        except Exception as e:
            print(f"[-] Encoding error: {e}", file=sys.stderr)
            return False

    def decode(self, stego_image: str, output_file: str = None) -> str:
        """
        Extracts a hidden message by reading the 32-bit prefix header first.
        """
        try:
            img = Image.open(stego_image).convert('RGB')
            arr = np.array(img, dtype=np.uint8)
            height, width, _ = arr.shape

            # 1. Extract first 32 bits for payload length
            header_bits = []
            for y in range(height):
                for x in range(width):
                    for c in range(3):
                        header_bits.append(str(arr[y, x, c] % 2))
                        if len(header_bits) == 32:
                            break
                    if len(header_bits) == 32:
                        break
                if len(header_bits) == 32:
                    break

            payload_len = int(''.join(header_bits), 2)
            total_target_bits = 32 + payload_len

            # 2. Extract payload bits
            all_bits = []
            for y in range(height):
                for x in range(width):
                    for c in range(3):
                        all_bits.append(str(arr[y, x, c] % 2))
                        if len(all_bits) >= total_target_bits:
                            break
                    if len(all_bits) >= total_target_bits:
                        break
                if len(all_bits) >= total_target_bits:
                    break

            message_bits = ''.join(all_bits[32:total_target_bits])
            bytes_list = [int(message_bits[i:i+8], 2) for i in range(0, len(message_bits), 8)]
            decoded_text = bytes(bytes_list).decode('utf-8', errors='replace')

            print(f"[+] Decoded message ({len(decoded_text)} chars):")
            print(f"    \"{decoded_text}\"")

            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(decoded_text)
                print(f"[+] Extracted message saved to file: {output_file}")

            return decoded_text
        except Exception as e:
            print(f"[-] Decoding error: {e}", file=sys.stderr)
            return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LSB Steganography Engine: Embed and retrieve hidden payloads.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enc_parser = subparsers.add_parser("encode", help="Hide a secret text message inside an image.")
    enc_parser.add_argument("-i", "--input", required=True, help="Input carrier image path (lossless PNG/BMP).")
    enc_group = enc_parser.add_mutually_exclusive_group(required=True)
    enc_group.add_argument("-m", "--message", help="Secret text string to hide.")
    enc_group.add_argument("-f", "--file", help="Path to text file containing the secret message.")
    enc_parser.add_argument("-o", "--output", required=True, help="Output stego image path.")

    dec_parser = subparsers.add_parser("decode", help="Extract a hidden message from a stego image.")
    dec_parser.add_argument("-i", "--input", required=True, help="Input stego image path.")
    dec_parser.add_argument("-o", "--output", help="Optional text file path to save extracted message.")

    args = parser.parse_args()
    engine = Steganography()

    if args.command == "encode":
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                secret_msg = f.read()
        else:
            secret_msg = args.message
        engine.encode(args.input, secret_msg, args.output)
    elif args.command == "decode":
        engine.decode(args.input, output_file=args.output)
