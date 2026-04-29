# core/timeline/checkpoint.py
from datetime import datetime
from typing import Dict, Any, List

class Checkpoint:
    def __init__(self, version: int, trait: str, state: Dict, adsr_phase: str, score: float):
        self.version = version
        self.timestamp = datetime.now().isoformat()
        self.trait = trait
        self.state = state
        self.adsr_phase = adsr_phase
        self.score = score
        self.metadata = {}

    def to_dict(self):
        return self.__dict__


class Timeline:
    def __init__(self):
        self.history: List[Checkpoint] = []
        self.current_version = 0

    def save(self, trait: str, state: Dict, adsr_phase: str, score: float):
        cp = Checkpoint(self.current_version, trait, state, adsr_phase, score)
        self.history.append(cp)
        self.current_version += 1
        return cp

    def jump_to(self, version: int) -> Dict:
        """Go back or forward in agent evolution"""
        for cp in self.history:
            if cp.version == version:
                return cp.state
        raise ValueError(f"Version {version} not found")