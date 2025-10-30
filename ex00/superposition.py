from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# Créer un circuit avec 1 qubit et 1 bit classique
qc = QuantumCircuit(1, 1)

# Appliquer la porte Hadamard pour créer une superposition
qc.h(0)
qc.measure(0, 0)

# Choisir le simulateur Aer
simulator = Aer.get_backend("aer_simulator")

# Exécuter le circuit
job = simulator.run(qc, shots=500)
result = job.result()

# Afficher les comptes de mesure
counts = result.get_counts(qc)

total = sum(counts.values())
proba = {state: count/total for state, count in counts.items()} #convertir en probabilite

plot_histogram(proba)
plt.savefig("histogram.png")



# import os
# from qiskit import QuantumCircuit
# from qiskit.transpiler import generate_preset_pass_manager
# from qiskit_ibm_runtime import SamplerV2 as Sampler

# circuit = QuantumCircuit(1)

# backend_real = service.list.busy(simulator=false)
# service = QiskitRuntimeService()

# pm = generate_preset_pass_manager(backend=backend)
# compiled_circuit = pm.run(circuit)

# sampler = Sampler(mode=backend)
# job = sampler.run([compiled_circuit])
# result=job.result()[0]

# counts=pub_result.data.c.get_counts()
# plot_histogram(counts)


