import os
import json
from google import genai

class NychLLM:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key and self.api_key.startswith("AIza"):
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.model = "gemini-2.0-flash-exp"
                print("✅ Gemini API connected")
            except:
                self.client = None
        else:
            print("⚠️  No valid GEMINI_API_KEY found. Using simulation mode.")

    def evaluate_trait(self, trait: str, state: dict) -> float:
        if not self.client:
            # Smart simulation fallback
            perf = state.get("performance", 0.5)
            coh = state.get("coherence", 0.5)
            return round(min(0.98, (perf * 0.6 + coh * 0.4) + 0.08), 3)

        try:
            prompt = f"Rate '{trait}' from 0.0-1.0. State: {state}. Return only number."
            response = self.client.models.generate_content(model=self.model, contents=prompt)
            score = float(response.text.strip())
            return max(0.1, min(0.99, score))
        except:
            return round(min(0.98, state.get("performance", 0.5) + 0.1), 3)

    def suggest_edit(self, trait: str, state: dict, intensity: float) -> dict:
        state = state.copy()
        
        if not self.client:
            # Strong simulation fallback
            state["performance"] = min(1.0, state.get("performance", 0.4) + 0.22 * intensity)
            state["coherence"] = min(1.0, state.get("coherence", 0.5) + 0.18 * intensity)
            state["stability"] = max(0.55, state.get("stability", 0.7) - 0.07 * intensity)
            return state

        try:
            prompt = f"""
            Improve agent on trait '{trait}' (intensity {intensity:.2f}).
            Current: {state}
            Return ONLY valid JSON with improved values.
            """
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            improved = response.parsed or {}
            state.update(improved)
            return state
        except:
            # Fallback already applied above
            return state
