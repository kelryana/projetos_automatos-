from dataclasses import dataclass, field
from typing import Optional
from maquina_turing import MaquinaTuring
from fita import Fita

@dataclass
class SimuladorTM:
    mt: MaquinaTuring
    fita: Fita = field(default_factory=Fita)
    current_state: Optional[str] = None
    step_count: int = 0
    timeout_steps: int = 1000

    def reset(self, entrada: str):
        entrada_syms = list(entrada)
        self.fita.blank = self.mt.blank
        self.fita.reset(entrada_syms)
        self.current_state = self.mt.q0
        self.step_count = 0

    def is_accept(self) -> bool:
        return self.current_state in self.mt.q_accept

    def is_reject(self) -> bool:
        return self.current_state in self.mt.q_reject

    def step(self):
        if self.is_accept() or self.is_reject():
            return None
        sym = self.fita.read()
        trs = self.mt.get_transitions(self.current_state, sym)
        if not trs:
            self.current_state = next(iter(self.mt.q_reject), None)
            return None
        
    # determinístico: pega a primeira
        tr = trs[0]
        self.fita.write(tr.write)
        self.fita.move(tr.move)
        self.current_state = tr.to_state
        self.step_count += 1
        return tr
    
        '''
        if tr is None:
            self.current_state = next(iter(self.mt.q_reject), None)
            return None
        self.fita.write(tr.write)
        self.fita.move(tr.move)
        self.current_state = tr.to_state
        self.step_count += 1
        return tr
'''