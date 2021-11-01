from qiskit import QuantumCircuit
from qiskit import Aer
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

if __name__ == '__main__':
    i0 = 0
    i1 = 0
    i2 = 0
    dist = [0.7, 0.1, 0.2]
    for _ in range(10000):

        choice = quantum_random_choice([0, 1, 2], dist)
        if choice == 0:
            i0 += 1
        elif choice == 1:
            i1 += 1
        else:
            i2 += 1
    
    print('i0:', i0)
    print('i1:', i1)
    print('i2:', i2)
