from core.adsr.gating import ADSRGate, ADSRPhase
from core.timeline.checkpoint import Timeline
from core.nych.protocol import NychSymbol
from typing import Callable, Dict, List

class RecursiveOptimizer:
    def __init__(self, max_iterations: int = 20):
        self.max_iterations = max_iterations
        self.timeline = Timeline()
        self.nych_symbols: List[NychSymbol] = []

    def optimize_trait(self, 
                      trait_name: str, 
                      initial_state: Dict, 
                      evaluate_fn: Callable[[Dict], float],
                      edit_fn: Callable[[Dict, float], Dict]):
        
        state = initial_state.copy()
        gate = ADSRGate(trait_name, ADSRPhase.ATTACK, intensity=1.0)
        
        print(f"\n🔧 Optimizing trait: {trait_name} using ADSR + Nych")

        for i in range(self.max_iterations):
            score = evaluate_fn(state)
            
            checkpoint = self.timeline.save(trait_name, state, gate.phase.value, score)
            
            print(f"  Step {i:2d} | Phase: {gate.phase.value.upper():7} | "
                  f"Score: {score:.3f} | Intensity: {gate.intensity:.2f}")

            # Apply Nych symbolic self-edit
            if score > 0.7:
                self.nych_symbols.append(NychSymbol(
                    name=f"OPT_{trait_name.upper()}_{i}",
                    meaning=f"Strengthen {trait_name}",
                    action="increase_coherence"
                ))

            if gate.phase == ADSRPhase.SUSTAIN and score >= 0.92:
                print("✅ Sweet spot reached!")
                break
                
            state = edit_fn(state, gate.intensity)
            
            # ADSR Phase Transition
            if i > self.max_iterations * 0.5:
                gate.phase = gate.next_phase()
                gate.intensity = max(0.3, gate.intensity * 0.75)

        return {
            "final_state": state,
            "best_version": max(self.timeline.history, key=lambda x: x.score).version,
            "timeline": self.timeline,
            "nych_symbols": self.nych_symbols
        }