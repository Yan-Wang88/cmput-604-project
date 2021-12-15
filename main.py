from crypto import BB84, RSA
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Secure data transmission.')
    parser.add_argument('--test_file_dir', default='test_files/', type=str)
    parser.add_argument('--received_file_dir', default='received_files/', type=str)
    parser.add_argument('--approx_key_length', default=1000, type=int)
    parser.add_argument('--rsa', action='store_true')
    args = parser.parse_args()
    
    if args.rsa:
        cipher = RSA
    else:
        cipher = BB84()

    _, _, files = next(os.walk(args.test_file_dir))
    for filename in files.reverse:
        print('processing:', filename)
        decrypted_file_bits = cipher.send_file(args.test_file_dir+filename, args.approx_key_length)
        with open(args.received_file_dir+filename[:-4]+'_received'+filename[-4:], 'wb') as f:
            decrypted_file_bits.tofile(f)

if __name__ == '__main__':
    main()
