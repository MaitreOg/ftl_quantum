from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


def oracle_const0(circuit):
    #f(x) = 0 
    pass  # pas d'action


def oracle_const1(circuit):
    #f(x) = 1 
    circuit.x(3)  # X sur le qubit auxiliaire


def oracle_fx(circuit):
    #f(x) = x
    circuit.cx(0, 3)  # CNOT : contrôle = qubit d'entrée, cible = auxiliaire
    circuit.cx(1, 3)  # CNOT : contrôle = qubit d'entrée, cible = auxiliaire
    circuit.cx(2, 3)  # CNOT : contrôle = qubit d'entrée, cible = auxiliaire


def oracle_notx(circuit):
    #f(x) = ¬x
    for i in range(3):
        circuit.x(i)
        circuit.cx(i, 3)
        circuit.x(i)
    

def deutschJozsa(oracle_func):
    qc = QuantumCircuit(4, 3)

    # Étape 1 : initialisation
    qc.x(3)        # auxiliaire en |1>

    # Étape 2 : Hadamard
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.h(3)
    qc.barrier()

    # Étape 3 : Oracle
    oracle_func(qc)  # on applique la fonction passée en paramètre
    qc.barrier()

    # Étape 4 : Hadamard final sur l'entrée
    qc.h(0)
    qc.h(1)
    qc.h(2)
    
    # Étape 5 : mesure de l'entrée
    qc.measure([0,1,2], [0,1,2])
    
    # Étape 6 : affichage du circuit
    #qc.draw("mpl")
    #plt.show()  

    # Simulation
    sim = Aer.get_backend("aer_simulator")
    job = sim.run(qc, shots=200) #envoi du circuit au backend puis repetition 500 fois
    result = job.result()
    counts = result.get_counts()
    total = sum(counts.values())  # ici = 200
    probs = {state: count / total for state, count in counts.items()}  # normalisation

    return probs


# Tests avec les 4 oracles
print("f(x)=0 :", deutschJozsa(oracle_const0))
print("f(x)=1 :", deutschJozsa(oracle_const1))
print("f(x)=x :", deutschJozsa(oracle_fx))
print("f(x)=¬x :", deutschJozsa(oracle_notx))
