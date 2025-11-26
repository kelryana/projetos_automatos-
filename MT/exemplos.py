from maquina_turing import MaquinaTuring, Transicao
from fita import Fita

BLANK = "λ"

def exemplo_incrementador_binario() -> MaquinaTuring:
    """
    Exemplo de Máquina de Turing que incrementa um número binário.
    Entrada: cadeia binária (ex.: 01101).
    Saída: número incrementado em 1.
    """
    mt = MaquinaTuring()
    mt.set_alphabets(sigma=["0", "1"], gamma=["0", "1", BLANK], blank=BLANK)

    # Estados
    for s in ["q0", "q1", "q_accept", "q_reject"]:
        mt.add_state(s)
    mt.set_initial("q0")
    mt.add_accept("q_accept")
    mt.add_reject("q_reject")

    # Transições
    # q0: move à direita até encontrar branco
    mt.add_transition(Transicao("q0", "0", "q0", "0", "R"))
    mt.add_transition(Transicao("q0", "1", "q0", "1", "R"))
    mt.add_transition(Transicao("q0", BLANK, "q1", BLANK, "L"))

    # q1: faz +1 com carry
    mt.add_transition(Transicao("q1", "0", "q_accept", "1", "S"))
    mt.add_transition(Transicao("q1", "1", "q1", "0", "L"))
    mt.add_transition(Transicao("q1", BLANK, "q_accept", "1", "S"))  # carry extra

    return mt
