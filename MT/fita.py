from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class Fita:
    blank: str = "λ"
    tape: Dict[int, str] = field(default_factory=dict)
    head: int = 0

    def reset(self, entrada: List[str]):
        self.tape.clear()
        for i, s in enumerate(entrada):
            self.tape[i] = s
        self.head = 0

    def read(self) -> str:
        return self.tape.get(self.head, self.blank)

    def write(self, symbol: str):
        self.tape[self.head] = symbol

    def move(self, direction: str):
        if direction == "L":
            self.head -= 1
        elif direction == "R":
            self.head += 1

    def window(self, radius: int = 10) -> List[Tuple[int, str]]:
        return [(i, self.tape.get(i, self.blank)) for i in range(self.head - radius, self.head + radius + 1)]
