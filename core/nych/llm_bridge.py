from google import genai
import os

class NychLLM:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.0-flash-exp"

    def evaluate_trait(self, trait: str, state: dict) -> float:
        """LLM scores the current state of a trait"""
        prompt = f"""
        Rate how well this agent performs on trait '{trait}' (0.0 to 1.0).
        Current state: {state}
        Return only a number between 0.0 and 1.0.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            score = float(response.text.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.65  # fallback

    def suggest_edit(self, trait: str, state: dict, intensity: float) -> dict:
        """LLM suggests symbolic improvement"""
        prompt = f"""
        Improve this agent on trait '{trait}' with intensity {intensity:.2f}.
        Current state: {state}
        Return valid JSON with improved state.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return response.parsed or state
        except:
            # Simple fallback edit
            state = state.copy()
            state["performance"] = min(1.0, state.get("performance", 0) + 0.15 * intensity)
            return state
