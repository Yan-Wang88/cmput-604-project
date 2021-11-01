from qiskit import Aer
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
from qiskit.quantum_info.states import statevector
import utility
import numpy as np
from qiskit.quantum_info import Statevector

class ClassicalChannel:
    def __init__(self) -> None:
        self._message = None

    def send(self, message_bits):
        self._message = message_bits
    
    def receive(self):
        assert self._message is not None
        message = self._message
        self._message = None

        return message
    
    def sniff(self):
        assert self._message is not None

        return self._message

class QuantumChannel:
    def __init__(self, error_rate) -> None:
        self._error_rate = error_rate
        self._state_vector = None

    '''
    def send(self, state_vector):
        self._state_vector = state_vector

    def receive(self):
        return self._state_vector
    '''

    def send(self, state_vector):
        # entangle with 2 other qubits to correct X error
        circ = QuantumCircuit(3)
        circ.initialize(state_vector, [0])
        circ.cnot(0, 1)
        circ.cnot(0, 2)

        # randomly apply X gate to simulate transmission error
        if utility.quantum_bernoulli_bit(self._error_rate):
            dist = np.array([1., 1., 1.])
            dist /= float(len(dist))
            choice = utility.quantum_random_choice([0, 1, 2], dist)
            # print('apply x to:', choice) # debug
            circ.x(choice)
            # circ.draw('mpl') # debug

        self._state_vector = Statevector(circ)

    def receive(self):
        circ = QuantumCircuit(5, 2)
        circ.initialize(self._state_vector, [0, 1, 2])
        self._state_vector = None # non-clone theorem
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
        # circ.draw('mpl') # debug

        backend = Aer.get_backend('statevector_simulator')
        job = backend.run(circ, shots=1)
        result = job.result()
        full_statevector = result.get_statevector()
        error_code = int(list(result.get_counts())[0], base=2)
        indices = [error_code << 3, (error_code << 3) + 1]

        return full_statevector[indices]
