from bitstring import Bits
from channel import QuantumChannel
import utility
from qiskit import QuantumCircuit
from qiskit import Aer
from qiskit.quantum_info import Statevector

class BB84:
    def generate_key(length):
        return utility.quantum_uniforum_bits(length)

    def encrypt(file_bits, key_bits):
        return file_bits ^ key_bits

    def decrypt(message_bits, key_bits):
        return message_bits ^ key_bits

    def encode_key_qubits(key_bits):
        state_vectors = []
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
    
    def decode_key_qubits(key_qubits):
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

class RSA:
    def encrypt(file_bits, key_bits):
        raise NotImplementedError()

if __name__ == '__main__':
    key_bits = BB84.generate_key(1000)
    key_qubits, basis_bits = BB84.encode_key_qubits(key_bits)
    quantumChannel = QuantumChannel(1)
    # print(key_bits) # debug
    # print(basis_bits) # debug
    received = []
    for qubit in key_qubits:
        quantumChannel.send(qubit)
        received += [quantumChannel.receive()]

    key_bits_2, basis_bits_2 = BB84.decode_key_qubits(received)

    count = 0
    for i in range(len(basis_bits_2)):
        if basis_bits[i] == basis_bits_2[i]:
            count += 1
    print(count/len(basis_bits_2))

    count = 0
    for i in range(len(key_bits_2)):
        if key_bits[i] == key_bits_2[i]:
            count += 1
    
    print(count/len(key_bits_2))


    key_qubits_2, basis_bits_2 = BB84.encode_key_qubits(key_bits_2)
    quantumChannel = QuantumChannel(0)
    received = []
    for qubit in key_qubits_2:
        quantumChannel.send(qubit)
        received += [quantumChannel.receive()]

    key_bits_3, basis_bits_3 = BB84.decode_key_qubits(received)

    count = 0
    for i in range(len(basis_bits_3)):
        if basis_bits[i] == basis_bits_3[i]:
            count += 1
    print(count/len(basis_bits_3))

    count = 0
    for i in range(len(key_bits_3)):
        if key_bits[i] == key_bits_3[i]:
            count += 1
    
    print(count/len(key_bits_3))