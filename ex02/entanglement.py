from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# Connexion IBM Quantum
service = QiskitRuntimeService(
    channel="ibm_quantum_platform",
    token="GvWYJ7mGgOpKqs1VJqzOMj4FjZMlJrgB1x7UePIgGDJL"
)
#service = QiskitRuntimeService(channel="ibm_quantum_platform")

# Choix du backend (vrai QPU)
backend = service.backend("ibm_marrakesh")

# creation du circuit
#la porte CNOT permet l intrication si les valeurs des 2 qubits sont diffrentes alors flib de qubit1
circuit = QuantumCircuit(2, 2)          #creation de 2 qubits
circuit.h(0)                            #applique une porte hardman (changement d etat de |0⟩ -> 1/√2 (|0⟩+ |1⟩)) 
circuit.cx(0, 1)                             # CNOT : qubit 0 = contrôle, qubit 1 = cible
circuit.measure([0,1], [0,1])                # mesure les 2 qubits                  

 # Transpilation pour le backend choisi
compiled = transpile(circuit, backend, optimization_level=3)

# Sampler
sampler = Sampler(mode=backend)

# Lancement du job
job = sampler.run([compiled], shots=500)

# Attente du résultat
result = job.result()
counts = result[0].data["c"].get_counts()

total = sum(counts.values())
proba = {state: count / total for state, count in counts.items()}

plot_histogram(proba)
plt.savefig("histogram.png")


