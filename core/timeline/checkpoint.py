from datetime import datetime
from typing import Dict, List

class Checkpoint:
    def __init__(self, version: int, trait: str, state: Dict, adsr_phase: str, score: float):
        self.version = version
        self.timestamp = datetime.now().isoformat()
        self.trait = trait
        self.state = state
        self.adsr_phase = adsr_phase
        self.score = score

    def to_dict(self):
        return self.__dict__


class Timeline:
    def __init__(self):
        self.history: List[Checkpoint] = []
        self.current_version = 0

    def save(self, trait: str, state: Dict, adsr_phase: str, score: float):
        cp = Checkpoint(self.current_version, trait, state.copy(), adsr_phase, score)
        self.history.append(cp)
        self.current_version += 1
        return cp

    def jump_to(self, version: int) -> Dict:
        for cp in self.history:
            if cp.version == version:
                print(f"⏪ Jumped to version {version} | Score: {cp.score:.3f} | Phase: {cp.adsr_phase}")
                return cp.state
        print(f"❌ Version {version} not found")
        return {}

    def get_best(self) -> Dict:
        if not self.history:
            return {}
        best = max(self.history, key=lambda x: x.score)
        print(f"⭐ Best version: {best.version} (Score: {best.score:.3f})")
        return best.state