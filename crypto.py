from math import isclose
from bitstring import BitString, Bits
from channel import QuantumChannel
import utility
from qiskit import QuantumCircuit
from qiskit import Aer
from qiskit.quantum_info import Statevector
import os

class BB84:
    def __init__(self) -> None:
        self._quantum_channel = QuantumChannel()

        self._alice_basis_vs_bob_basis_log = open('log_files/alice_basis_vs_bob_basis.log', 'a')
        self._alice_key_vs_bob_key_log = open('log_files/alice_key_vs_bob_key.log', 'a')
        self._alice_good_bits_vs_bob_good_bits_log = open('log_files/alice_good_bits_vs_bob_good_bits.log', 'a')
        self._alice_sample_bits_vs_bob_sample_bits_log = open('log_files/alice_sample_bits_vs_bob_sample_bits.log', 'a')
        self._alice_basis_vs_eve_basis_log = open('log_files/alice_basis_vs_eve_basis.log', 'a')
        self._alice_key_vs_eve_key_log = open('log_files/alice_key_vs_eve_key.log', 'a')

    def send_file(self, filename, approx_key_length):
        file_bits = Bits(filename=filename)

        header_string = '='*20+filename+'='*20+'\n'
        self._alice_basis_vs_bob_basis_log.write(header_string)
        self._alice_key_vs_bob_key_log.write(header_string)
        self._alice_good_bits_vs_bob_good_bits_log.write(header_string)
        self._alice_sample_bits_vs_bob_sample_bits_log.write(header_string)
        self._alice_basis_vs_eve_basis_log.write(header_string)
        self._alice_key_vs_eve_key_log.write(header_string)

        remaining_bits = len(file_bits)
        key_length = 4*approx_key_length
        decrypted_file_bits = BitString()

        # sending loop
        while remaining_bits > 0:
            print('remaining bits:', remaining_bits)
            # key distribution
            # alice generate a new key
            alice_key_bits = utility.quantum_uniforum_bits(key_length)
            self._distribute_key(alice_key_bits)

            if self._check_for_eveasdroppers(): # when there is an eavesdropper, discard the current key
                continue

            # encrypt file segments
            start_loc = len(file_bits) - remaining_bits
            end_loc = start_loc + len(self._alice_encrypt_key)

            if end_loc > len(file_bits):
                end_loc = len(file_bits)
                self._alice_encrypt_key = self._alice_encrypt_key[:end_loc-start_loc]

            encrypted_bits = file_bits[start_loc:end_loc] ^ self._alice_encrypt_key
            remaining_bits -= len(self._alice_encrypt_key)
            decrypted_file_bits.append(encrypted_bits ^ self._bob_decrypt_key[:len(encrypted_bits)])

        return decrypted_file_bits

    def _distribute_key(self, alice_key_bits):
        alice_key_qubits, alice_basis_bits = self._encode_key_qubits(alice_key_bits)

        received = []
        for qubit in alice_key_qubits:
            self._quantum_channel.send(qubit)
            received += [self._quantum_channel.receive()]

        eveasdropper_prob = 0.5
        eveasdropper = utility.quantum_bernoulli_bit(eveasdropper_prob)
        if eveasdropper:
            print('Eve tries to intercept key bits...')
            eve_key_bits, eve_basis_bits = self._decode_key_qubits(received)

            count = 0
            for i in range(len(eve_basis_bits)):
                if alice_basis_bits[i] == eve_basis_bits[i]:
                    count += 1

            self._alice_basis_vs_eve_basis_log.write(str(100*count/len(eve_basis_bits))+'\n')

            count = 0
            for i in range(len(eve_basis_bits)):
                if eve_key_bits[i] == alice_key_bits[i]:
                    count += 1

            self._alice_key_vs_eve_key_log.write(str(100*count/len(eve_key_bits))+'\n')
            
            eve_key_qubits, _ = self._encode_key_qubits(eve_key_bits, eve_basis_bits)

            received = []
            for qubit in eve_key_qubits:
                self._quantum_channel.send(qubit)
                received += [self._quantum_channel.receive()]

        bob_key_bits, bob_basis_bits = self._decode_key_qubits(received)
        count = 0
        for i in range(len(bob_basis_bits)):
            if alice_basis_bits[i] == bob_basis_bits[i]:
                count += 1

        self._alice_basis_vs_bob_basis_log.write(str(100*count/len(bob_basis_bits))+'\n')

        assert count != 0 # extremely low probability

        count = 0
        for i in range(len(bob_key_bits)):
            if alice_key_bits[i] == bob_key_bits[i]:
                count += 1
        
        self._alice_key_vs_bob_key_log.write(str(100*count/len(bob_key_bits))+(', True\n' if eveasdropper else ', False\n'))

        alice_good_bits = []
        bob_good_bits = []
        for i in range(len(alice_basis_bits)):
            if alice_basis_bits[i] == bob_basis_bits[i]:
                alice_good_bits.append('1' if alice_key_bits[i] else '0')
                bob_good_bits.append('1' if bob_key_bits[i] else '0')

        self._alice_encrypt_key = Bits('0b'+''.join(alice_good_bits))
        self._bob_decrypt_key = Bits('0b'+''.join(bob_good_bits))

        count = 0
        for i in range(len(self._alice_encrypt_key)):
            if self._alice_encrypt_key[i] == self._bob_decrypt_key[i]:
                count += 1

        success_rate = count/len(self._alice_encrypt_key)
        self._alice_good_bits_vs_bob_good_bits_log.write(str(100*success_rate)+(', True\n' if eveasdropper else ', False\n')) # good bits success rate

    def _check_for_eveasdroppers(self):
        # sample the even bits
        alice_sample_bits = self._alice_encrypt_key[::2]
        bob_sample_bits = self._bob_decrypt_key[::2]

        count = 0
        for i in range(len(alice_sample_bits)):
            if alice_sample_bits[i] == bob_sample_bits[i]:
                count += 1

        success_rate = count/len(alice_sample_bits)
        self._alice_sample_bits_vs_bob_sample_bits_log.write(str(100*success_rate)) # good bits success rate

        if isclose(success_rate, 1.0):
            self._alice_sample_bits_vs_bob_sample_bits_log.write(', False\n')
            self._alice_encrypt_key = self._alice_encrypt_key[1::2]
            self._bob_decrypt_key = self._bob_decrypt_key[1::2]
            return False
        else:
            print('warning: eavesdropper detected!')
            self._alice_sample_bits_vs_bob_sample_bits_log.write(', True\n')
            return True

    def _encode_key_qubits(self, key_bits, basis_bits=None):
        state_vectors = []
        if basis_bits is None:
            basis_bits = utility.quantum_uniforum_bits(len(key_bits))

        for i in range(len(key_bits)):
            if basis_bits[i]: # use X basis
                if key_bits[i]: # encode 1 to |->
                    circ = QuantumCircuit(1)
                    circ.x(0)
                    circ.h(0)
                    state_vectors += [Statevector(circ)]
                else: # encode 0 to |+>
                    circ = QuantumCircuit(1)
                    circ.h(0)
                    state_vectors += [Statevector(circ)]
            else: # use Z basis
                if key_bits[i]: # encode 1 to |1>
                    circ = QuantumCircuit(1)
                    circ.x(0)
                    state_vectors += [Statevector(circ)]
                else:
                    circ = QuantumCircuit(1)
                    state_vectors += [Statevector(circ)]
        
        return state_vectors, basis_bits
    
    def _decode_key_qubits(self, key_qubits):
        basis_bits = utility.quantum_uniforum_bits(len(key_qubits))
        backend = Aer.get_backend('statevector_simulator')
        key_bits = Bits(0)

        for i in range(len(key_qubits)):
            if basis_bits[i]: # measure on X basis
                circ = QuantumCircuit(1)
                circ.initialize(key_qubits[i], [0])
                circ.h(0)
                circ.measure_all()
                job = backend.run(circ, shots=1)
                result = job.result()
                key_bits += Bits('0b'+list(result.get_counts())[0])
            else: # measure on Z basis
                circ = QuantumCircuit(1)
                circ.initialize(key_qubits[i], [0])
                circ.measure_all()
                job = backend.run(circ, shots=1)
                result = job.result()
                key_bits += Bits('0b'+list(result.get_counts())[0])

        return key_bits, basis_bits

    def __del__(self):
        self._alice_basis_vs_bob_basis_log.close()
        self._alice_key_vs_bob_key_log.close()
        self._alice_good_bits_vs_bob_good_bits_log.close()
        self._alice_sample_bits_vs_bob_sample_bits_log.close()
        self._alice_basis_vs_eve_basis_log.close()
        self._alice_key_vs_eve_key_log.close()

class RSA:
    def encrypt(file_bits, key_bits):
        raise NotImplementedError()

if __name__ == '__main__':
    cipher = BB84()

    _, _, files = next(os.walk('test_files'))
    for filename in files:
        decrypted_file_bits = cipher.send_file(filename, 1000)
        with open(filename[:-4]+'_received'+filename[-4:], 'wb') as f:
            decrypted_file_bits.tofile(f)
