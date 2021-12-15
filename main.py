from crypto import BB84, RSA
import argparse
from bitstring import Bits


def main():
    parser = argparse.ArgumentParser(description='Secure data transmission.')
    parser.add_argument('--file', default='test.txt', type=str)
    parser.add_argument('--key_length', default=6, type=int)
    parser.add_argument('--rsa', action='store_true')
    parser.add_argument('--sniffer', action='store_true')
    args = parser.parse_args()
    
    if args.rsa:
        cipher = RSA
    else:
        cipher = BB84()

    decrypted_file_bits = cipher.send_file('long_text.txt', 1000)

    
if __name__ == '__main__':
    main()
