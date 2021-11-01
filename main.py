from crypto import BB84, RSA
import argparse
from bitstring import Bits
from channel import ClassicalChannel

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
        cipher = BB84
    
    # experiment setup
    classicalChannel = ClassicalChannel()

    # alice setup
    file_bits = Bits(filename=args.file)
    remaining_bits = len(file_bits)
    if args.key_length == 0:
        key_length = len(file_bits)
    else:
        key_length = args.key_length

    # sniffer setup
    intercepted_file_bits = Bits(0)

    # bob setup
    received_file_bits = Bits(0)

    # communication loop
    while remaining_bits > 0:
        # key distribution
        # alice generate a new key
        key_bits = cipher.generate_key(min(key_length, remaining_bits))
        # encrypt file segments
        start_loc = len(file_bits) - remaining_bits
        end_loc = start_loc + len(key_bits)
        encrypted_seg_bits = cipher.encrypt(file_bits[start_loc:end_loc], key_bits)
        # send the new key to bob
        classicalChannel.send(key_bits)
        del key_bits 

        # sniffer intercept the new key if present
        if args.sniffer:
            intercepted_key_bits = classicalChannel.sniff()

        # bob receive the new key
        received_key_bits = classicalChannel.receive()

        # alice send the file segment
        classicalChannel.send(encrypted_seg_bits)
        remaining_bits -= len(encrypted_seg_bits)
        del encrypted_seg_bits

        # sniffer intercept the file segment if present
        if args.sniffer:
            intercepted_file_segment = classicalChannel.sniff()
            intercepted_file_bits += cipher.decrypt(intercepted_file_segment, intercepted_key_bits)

        # bob receive the file segment
        received_file_segment = classicalChannel.receive()
        received_file_bits += cipher.decrypt(received_file_segment, received_key_bits)

    del file_bits

    # save results
    if args.sniffer:
        with open('sniffed_'+args.file, 'wb') as f:
            intercepted_file_bits.tofile(f)

    with open('received_'+args.file, 'wb') as f:
        received_file_bits.tofile(f)
    
if __name__ == '__main__':
    main()