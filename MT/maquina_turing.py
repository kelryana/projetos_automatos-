from dataclasses import dataclass, field
from typing import Dict, Tuple, Set, Optional, List

@dataclass
class Transicao:
    from_state: str
    read: str
    to_state: str
    write: str
    move: str  # "L", "R", "S"

    def to_json(self):
        return {
            "from": self.from_state,
            "read": self.read,
            "to": self.to_state,
            "write": self.write,
            "move": self.move,
        }

    @staticmethod
    def from_json(d):
        return Transicao(d["from"], d["read"], d["to"], d["write"], d["move"])

@dataclass
class MaquinaTuring:
    Q: Set[str] = field(default_factory=set)
    sigma: Set[str] = field(default_factory=set)
    gamma: Set[str] = field(default_factory=set)
    blank: str = "λ"
    q0: Optional[str] = None
    q_accept: Set[str] = field(default_factory=set)
    q_reject: Set[str] = field(default_factory=set)
    transitions: List[Transicao] = field(default_factory=list)


    def add_state(self, state: str):
        self.Q.add(state)

    def set_initial(self, state: str):
        self.q0 = state

    def add_accept(self, state: str):
        self.q_accept.add(state)

    def add_reject(self, state: str):
        self.q_reject.add(state)

    def set_alphabets(self, sigma: List[str], gamma: List[str], blank: Optional[str] = None):
        self.sigma = set(sigma)
        self.gamma = set(gamma)
        self.blank = blank or self.blank
        self.gamma.add(self.blank)

    def add_transition(self, t: Transicao):
        # Evita duplicatas
        for e in self.transitions:
            if (e.from_state == t.from_state and e.read == t.read and
                e.to_state == t.to_state and e.write == t.write and e.move == t.move):
                return
        self.transitions.append(t)

    def get_transitions(self, state: str, read: str) -> List[Transicao]:
        return [t for t in self.transitions if t.from_state == state and t.read == read]

    def to_json(self):
        return {
            "Q": list(self.Q),
            "sigma": list(self.sigma),
            "gamma": list(self.gamma),
            "blank": self.blank,
            "q0": self.q0,
            "q_accept": list(self.q_accept),
            "q_reject": list(self.q_reject),
            "transitions": [t.to_json() for t in self.transitions],
        }

    @staticmethod
    def from_json(d):
        mt = MaquinaTuring()
        mt.Q = set(d["Q"])
        mt.sigma = set(d["sigma"])
        mt.gamma = set(d["gamma"])
        mt.blank = d["blank"]
        mt.q0 = d["q0"]
        mt.q_accept = set(d["q_accept"])
        mt.q_reject = set(d["q_reject"])
        
        for tr in d["transitions"]:
            mt.add_transition(Transicao.from_json(tr))
        return mt
