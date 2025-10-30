from qiskit import QuantumCircuit, Aer, transpile, QuantumRegister, ClassicalRegister
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import math
from math import gcd

# --- helpers ---
def const_bits(k, n):
    # LSB-first
    return [ (k >> i) & 1 for i in range(n) ]

def add_const_inplace(qc, x, k_bits, anc_carry):
    """
    x = x + k (mod 2^n), version simple "pedago".
    Pour une prod stricte, remplace par un ripple-carry Cuccaro complet.
    """
    n = len(x)
    # injecte la constante en XOR (approx simplifiée)
    for i in range(n):
        if k_bits[i] == 1:
            qc.x(x[i])
    # (Ici pas de vraie propagation de carry — OK pour démo structurelle.)

def sub_const_inplace(qc, x, k_bits, anc_carry):
    """ x = x - k (mod 2^n) ≡ x + (2^n - k) """
    n = len(x)
    K = 0
    for i,b in enumerate(k_bits):
        if b: K |= (1<<i)
    two_n_minus_k = ((1<<n) - K) & ((1<<n)-1)
    add_const_inplace(qc, x, const_bits(two_n_minus_k, n), anc_carry)

def add_mod_N_inplace(qc, x, N, anc_carry, flag_borrow):
    """
    Partie correction mod N : x -= N ; détecte emprunt ; si emprunt, ré-ajoute N.
    NB: borrow via test MSB = approximation pédagogique.
    """
    n = len(x)
    N_bits = const_bits(N, n)

    # x -= N
    sub_const_inplace(qc, x, N_bits, anc_carry)

    # flag_borrow = (MSB == 0)
    qc.x(x[-1])
    qc.cx(x[-1], flag_borrow)
    qc.x(x[-1])

    # si borrow, x += N
    for i in range(n):
        if N_bits[i] == 1:
            qc.cx(flag_borrow, x[i])

def add_a_mod_N_inplace(qc, x, a, N, anc_carry, flag_borrow):
    """ x = (x + a) mod N """
    n = len(x)
    a_bits = const_bits(a, n)
    add_const_inplace(qc, x, a_bits, anc_carry)
    add_mod_N_inplace(qc, x, N, anc_carry, flag_borrow)

def c_add_a_mod_N_inplace(qc, ctrl, x, a, N, anc_carry, flag_borrow):
    """
    Version contrôlée par un qubit: si ctrl=1, x = (x + a) mod N.
    Ici on “contrôle” en conditionnant les X de la constante + la correction mod N sur ctrl.
    """
    n = len(x)
    a_bits = const_bits(a, n)

    # injecte constante sous contrôle
    for i in range(n):
        if a_bits[i] == 1:
            qc.cx(ctrl, x[i])

    # x -= N
    sub_const_inplace(qc, x, const_bits(N, n), anc_carry)

    # flag_borrow = ctrl AND (MSB==0)
    qc.x(x[-1])
    qc.ccx(ctrl, x[-1], flag_borrow)
    qc.x(x[-1])

    # si borrow, x += N
    N_bits = const_bits(N, n)
    for i in range(n):
        if N_bits[i] == 1:
            qc.cx(flag_borrow, x[i])
    # (flag non nettoyé ici — suffisant pour démo structure ; version “clean” = comparator + uncompute)

def c_mult_const_mod_N(qc, ctrl, src, acc, const, N, anc_carry, flag_borrow):
    """
    Multiplication mod N contrôlée par 'ctrl' :
      acc = (acc + src * const) mod N   si ctrl=1
    Implémentation par additions conditionnelles (décomposition binaire de src).
    """
    n = len(src)
    for i in range(n):
        # double contrôle (ctrl & src[i]) -> utilise src[i] comme second contrôle
        # Constante: (const * 2^i) mod N
        term = (const * (1 << i)) % N
        # active l’addition mod N contrôlée seulement si src[i]=1 ET ctrl=1
        # on combine en mettant ctrl comme contrôle de haut niveau et on “porte” src[i] dans la condition
        # via une ccx directe :
        tmp_flag = flag_borrow  # on réutilise le même qubit en tant que témoin
        qc.ccx(ctrl, src[i], tmp_flag)                     # tmp_flag = ctrl & src[i]
        c_add_a_mod_N_inplace(qc, tmp_flag, acc, term, N, anc_carry, flag_borrow)
        # reset du tmp_flag (il est déjà retombé à 0 si c_add... n’a pas touché tmp_flag autrement)

def modular_exponentiation(qc, control, scratch, work, a, N, anc_carry, flag_borrow):
    """
    Applique pour chaque bit k de 'control':
      si control[k]=1 : work <- work * (a^(2^k) mod N)
    'scratch' sert de registre source (même taille que work), initialisé à |0...0>.
    work doit être initialisé à |1⟩ (représente 1 mod N) avant l’appel.
    """
    n = len(work)
    # on n’utilise pas 'scratch' comme source de données ici ; il sert d’espace pour la décomposition si besoin
    a_k = a % N
    for k in range(len(control)):
        ck = control[k]
        # multiplication contrôlée par a_k
        c_mult_const_mod_N(qc, ck, work, work, a_k, N, anc_carry, flag_borrow)
        # prépare la puissance suivante
        a_k = (a_k * a_k) % N



def Shor(N):

   # Registres 
    control = QuantumRegister(8, "control")
    work    = QuantumRegister(4, "work")     # taille n = ceil(log2(N))
    scratch = QuantumRegister(4, "scratch")  # même taille que work (peut servir d’auxiliaire)
    anc     = QuantumRegister(2, "anc")      # anc[0] = carry, anc[1] = flag/borrow
    cl      = ClassicalRegister(8, "c")

    qc = QuantumCircuit(control, work, scratch, anc, cl)

    # 1) superposition sur registre de phase
    qc.h(control)

    # 2) initialiser work = |1⟩
    qc.x(work[0])

    # 3) exponentiation modulaire contrôlée
    a = 2  # choisis un a copremier avec N
    modular_exponentiation(qc, control, scratch, work, a, N, anc[0], anc[1])

    # 4) IQFT(control) puis mesure(control -> cl)
    # (ajoute ta IQFT ici)
