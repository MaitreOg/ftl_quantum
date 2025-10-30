from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ---------------------
# ORACLES
# ---------------------
def oracle_const0(circuit):
    # f(x) = 0
    pass  # pas d'action


def oracle_const1(circuit):
    # f(x) = 1
    circuit.x(3)  # X sur le qubit auxiliaire


def oracle_fx(circuit):
    # f(x) = x
    circuit.cx(0, 3)
    circuit.cx(1, 3)
    circuit.cx(2, 3)


def oracle_notx(circuit):
    # f(x) = ¬x
    for i in range(3):
        circuit.x(i)
        circuit.cx(i, 3)
        circuit.x(i)


# ---------------------
# ALGORITHME DEUTSCH–JOZSA
# ---------------------
def deutschJozsa(oracle_func, backend):
    qc = QuantumCircuit(4, 3)

    # Initialisation
    qc.x(3)
    for i in range(4):
        qc.h(i)
    qc.barrier()

    # Oracle
    oracle_func(qc)
    qc.barrier()

    # Hadamard final
    for i in range(3):
        qc.h(i)
    qc.measure([0, 1, 2], [0, 1, 2])

    # Transpilation pour le backend choisi
    compiled = transpile(qc, backend, optimization_level=3)

    # ✅ Sampler nouvelle API Qiskit Runtime 0.43
    sampler = Sampler(mode=backend)

    # Lancement du job
    job = sampler.run([compiled], shots=200)

    # Suivi d’état (optionnel mais utile)
    print("⏳ Exécution en cours sur", backend.name)
    print("Job ID:", job.job_id())

    # Attente du résultat
    result = job.result()
    counts = result[0].data["c"].get_counts()

    total = sum(counts.values())
    probs = {state: count / total for state, count in counts.items()}
    return probs
# ---------------------
# PROGRAMME PRINCIPAL
# ---------------------
if __name__ == "__main__":
    # Connexion IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform")

    # Choix du backend (vrai QPU)
    backend = service.backend("ibm_brisbane")

    print("\nExécution de Deutsch–Jozsa sur", backend.name)
    print("f(x)=0 :", deutschJozsa(oracle_const0, backend))
    print("f(x)=1 :", deutschJozsa(oracle_const1, backend))
    print("f(x)=x :", deutschJozsa(oracle_fx, backend))
    print("f(x)=¬x :", deutschJozsa(oracle_notx, backend))
