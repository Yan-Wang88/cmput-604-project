from qiskit import QuantumCircuit
from qiskit import Aer
from qiskit.circuit.classicalregister import ClassicalRegister
from qiskit.circuit.quantumregister import AncillaRegister, QuantumRegister
from bitstring import Bits
import math
import numpy as np

def quantum_uniforum_bits(length):
    circ = QuantumCircuit(length)
    for i in range(length):
        circ.h(i)

    circ.measure_all()

    backend = Aer.get_backend('qasm_simulator')
    job = backend.run(circ, shots=1)
    result = job.result()

    return Bits('0b'+list(result.get_counts())[0])

def quantum_bernoulli_bit(p):
    assert 0 <= p <= 1
    circ = QuantumCircuit(1)
    theta = math.asin(p**0.5)
    circ.ry(2*theta, 0)
    circ.measure_all()

    backend = Aer.get_backend('qasm_simulator')
    job = backend.run(circ, shots=1)
    result = job.result()
    return 1 if list(result.get_counts())[0] == '1' else 0 

def quantum_random_choice(items, dist):
    dist = np.array(dist)

    while len(items) > 1:
        if quantum_bernoulli_bit(dist[0]):
            return items[0]

        dist = dist[1:] / (1 - dist[0])
        items = items[1:]

    return items[0]

def bit_flip_recovery_circ(name):
    qr = QuantumRegister(3, name)
    ar = AncillaRegister(2, name+'_error_code_ar')
    cr = ClassicalRegister(2, name+'_error_code_cr')
    circ = QuantumCircuit(qr, ar, cr)
    circ.cnot(0, 3)
    circ.cnot(1, 3)
    circ.cnot(1, 4)
    circ.cnot(2, 4)
    circ.cnot(3, 0)
    circ.cnot(4, 2)
    circ.ccx(3, 4, 0)
    circ.ccx(3, 4, 1)
    circ.ccx(3, 4, 2)

    # unentangle the code qubits
    circ.cnot(0, 2)
    circ.cnot(0, 1)
    circ.measure([3, 4], [0, 1])

    return circ

def bit_flip_encode_circ(name):
    qr = QuantumRegister(3, name)
    circ = QuantumCircuit(qr)
    circ.cnot(0, 1)
    circ.cnot(0, 2)
    return circ

if __name__ == '__main__':
    dist = np.array([1.]*3)
    dist /= float(len(dist))
    x = 0
    y = 0
    z = 0
    for _ in range(1000):
        error = quantum_random_choice(['x', 'y', 'z'], dist)
        
        if error == 'x':
            x += 1
        elif error == 'y':
            y += 1
        elif error == 'z':
            z += 1
        else:
            raise NotImplementedError()
    
    print('x:',x)
    print('y:',y)
    print('z:',z)