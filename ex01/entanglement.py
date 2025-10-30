from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# creation du circuit
#la porte CNOT permet l intrication si les valeurs des 2 qubits sont diffrentes alors flib de qubit1
circuit = QuantumCircuit(2, 2)          #creation de 2 qubits
circuit.h(0)                            #applique une porte hardman (changement d etat de |0⟩ -> 1/√2 (|0⟩+ |1⟩)) 
circuit.cx(0, 1)                             # CNOT : qubit 0 = contrôle, qubit 1 = cible
circuit.measure([0,1], [0,1])                # mesure les 2 qubits                  

simulator = Aer.get_backend("aer_simulator")
job = simulator.run(circuit, shots=500) #envoi du circuit au backend puis repetition 500 fois
result = job.result()
counts = result.get_counts()

total = sum(counts.values())
proba = {state: count/total for state, count in counts.items()} #convertir en probabilite

plot_histogram(proba)
plt.savefig("histogram.png")

