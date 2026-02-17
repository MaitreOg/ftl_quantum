from qiskit_ibm_runtime import QiskitRuntimeService

# Sauvegarder le compte (à faire UNE SEULE FOIS)
QiskitRuntimeService.save_account(
    token="GvWYJ7mGgOpKqs1VJqzOMj4FjZMlJrgB1x7UePIgGDJL",   # ta clé API copiée du dashboard
    #instance="CRN",                  
    set_as_default=True,
    overwrite=True
)