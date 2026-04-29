from enum import Enum
from typing import Dict, Any

class ADSRPhase(Enum):
    ATTACK = "attack"      # Aggressive optimization
    DECAY = "decay"        # Reduce intensity
    SUSTAIN = "sustain"    # Stable refined state
    RELEASE = "release"    # Graceful rollback/transition

class ADSRGate:
    def __init__(self, trait: str, phase: ADSRPhase, intensity: float = 1.0):
        self.trait = trait
        self.phase = phase
        self.intensity = intensity
        self.iteration = 0

    def next_phase(self) -> ADSRPhase:
        order = [ADSRPhase.ATTACK, ADSRPhase.DECAY, ADSRPhase.SUSTAIN, ADSRPhase.RELEASE]
        idx = order.index(self.phase)
        return order[(idx + 1) % len(order)]
