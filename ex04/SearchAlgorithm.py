from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

def oracle_example(qc):
    # Schéma donné : q0 et q1 contrôlent, q2 est la cible
    qc.h(2)              
    qc.ccx(0, 1, 2)      
    qc.h(2)              

def diffuser(qc, qubits):
    qc.h(qubits)
    qc.x(qubits)

    t = qubits[-1]
    c = qubits[:-1]

    qc.h(t)
    qc.mcx(c, t)
    qc.h(t)

    qc.x(qubits)
    qc.h(qubits)


def search(n, oracle_func):
    if n < 2:
        raise ValueError(f"Le nombre de qubits doit être >= 2, reçu : {n}")
    #init
    qc = QuantumCircuit(n, n)

    for i in range(n):
        qc.h(i)
    qc.barrier()

    for i in range(n - 1):
        #oracle
        oracle_func(qc)  # on applique la fonction passée en paramètre
        qc.barrier()
        #difuser
        diffuser(qc, list(range(n)))

    qc.measure(range(n), range(n))

    simulator = Aer.get_backend("aer_simulator")
    job = simulator.run(qc, shots=500) #envoi du circuit au backend puis repetition 500 fois
    result = job.result()
    counts = result.get_counts()

    total = sum(counts.values())
    proba = {state: count/total for state, count in counts.items()} #convertir en probabilite

    plot_histogram(proba)
    plt.savefig("histogram.png")

search(3, oracle_example)
