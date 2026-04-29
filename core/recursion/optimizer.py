from core.adsr.gating import ADSRGate, ADSRPhase
from core.timeline.checkpoint import Timeline
from core.nych.protocol import NychSymbol
from core.nych.llm_bridge import NychLLM
from typing import Dict

class RecursiveOptimizer:
    def __init__(self, max_iterations: int = 12):
        self.max_iterations = max_iterations
        self.timeline = Timeline()
        self.llm = NychLLM()
        self.nych_symbols = []

    def optimize_trait(self, trait_name: str, initial_state: Dict):
        state = initial_state.copy()
        gate = ADSRGate(trait_name, ADSRPhase.ATTACK, intensity=1.0)

        print(f"\n🔧 Optimizing trait: {trait_name} [LLM Powered]")

        for i in range(self.max_iterations):
            score = self.llm.evaluate_trait(trait_name, state)
            
            self.timeline.save(trait_name, state, gate.phase.value, score)
            
            print(f"  Step {i:2d} | Phase: {gate.phase.value.upper():7} | "
                  f"Score: {score:.3f} | Intensity: {gate.intensity:.2f}")

            if gate.phase == ADSRPhase.SUSTAIN and score >= 0.90:
                print("✅ Sweet spot reached!")
                break

            # Real LLM edit
            state = self.llm.suggest_edit(trait_name, state, gate.intensity)

            # Nych Symbol
            self.nych_symbols.append(NychSymbol(
                f"OPT_{trait_name.upper()}_{i}",
                f"Improve {trait_name}",
                "increase_coherence"
            ))

            # ADSR Transition
            if i > self.max_iterations * 0.45:
                gate.phase = gate.next_phase()
                gate.intensity = max(0.25, gate.intensity * 0.78)

        best_state = self.timeline.get_best()
        best_version = max(self.timeline.history, key=lambda x: x.score).version

        return {
            "final_state": state,
            "best_state": best_state,
            "best_version": best_version,
            "timeline": self.timeline,
            "nych_symbols": self.nych_symbols
        }