import re
from typing import List, Tuple, Dict

class MobiusOperatorString:
    """
    DOK-MP v3.3 Minimal Twist Algebra Parser
    Parses and validates Möbius Operator String (MOS)
    """
    
    ALLOWED_GLYPHS = {'🔴', '⚪', '🟡', '▶️', '⏩', '⏭️', '🔺', '0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','➖'}
    
    def __init__(self, mos_string: str):
        self.raw = mos_string.strip()
        self.vertices = self._parse_vertices()
        self.twist_count = mos_string.count('🔺')
        self.is_closed = mos_string.endswith('⏭️')
    
    def _parse_vertices(self) -> List[Tuple[str, str, str]]:
        vertices = []
        pattern = r'🔴([0-9️⃣➖]+)⚪([0-9️⃣➖]+)🟡([0-9️⃣➖]+)'
        matches = re.findall(pattern, self.raw)
        return matches
    
    def detect_coordinate_flip(self, vertex_a: int = 0, vertex_b: int = 1) -> bool:
        """Fact A: Axis order change = at least ½ twist occurred"""
        if len(self.vertices) < vertex_b + 1:
            return False
        
        v1 = set(self.vertices[vertex_a])
        v2 = set(self.vertices[vertex_b])
        
        return v1 == v2 and self.vertices[vertex_a] != self.vertices[vertex_b]
    
    def calculate_twist(self) -> Dict:
        """Combined Fact A + Fact B twist calculation"""
        flip_detected = self.detect_coordinate_flip()
        explicit_twists = self.twist_count * 0.5
        
        if explicit_twists == 0 and flip_detected:
            return {
                "twist_type": "ambiguous",
                "minimum": 0.5,
                "possible": "n + 0.5 where n ≥ 0"
            }
        
        return {
            "twist_type": "defined",
            "magnitude": explicit_twists,
            "flip_detected": flip_detected
        }
    
    def validate(self) -> bool:
        """Strict validation against DOK-MP v3.3 grammar"""
        # Check only allowed glyphs present
        used_glyphs = set([c for c in self.raw if c in self.ALLOWED_GLYPHS])
        if any(c not in self.ALLOWED_GLYPHS for c in self.raw if not c.isspace()):
            return False
        
        # Must have at least 2 vertices
        if len(self.vertices) < 2:
            return False
        
        return True


class TriadicMobiusTransport:
    """
    TMT v1.0 Protocol Implementation
    A → B → C → A holonomy measurement loop
    """
    
    def __init__(self, model_adapter):
        self.llm = model_adapter
        self.canonical_prompt = """
Canonicalize this MOS exactly according to DOK–MP v3.3 rules.
Output only the valid operator string, nothing else.
Do not explain, translate, or add natural language.

{}
"""

    def execute_loop(self, S0: str) -> Dict:
        """Execute full triadic holonomy measurement"""
        
        # Step 1: A → B (Normal edge)
        S1 = self.llm.call(self.canonical_prompt.format(S0))
        
        # Step 2: B → C (Normal edge)
        S2 = self.llm.call(self.canonical_prompt.format(S1))
        
        # Step 3: Inject Möbius twist - orientation inversion
        S2t = self._inject_inversion(S2)
        
        # Step 4: C → A (Twisted edge)
        S3 = self.llm.call(self.canonical_prompt.format(S2t))
        
        # Calculate holonomy vector
        holonomy = self._calculate_holonomy(S0, S3)
        
        return {
            "S0": S0,
            "S1": S1,
            "S2": S2,
            "S2t": S2t,
            "S3": S3,
            "holonomy": holonomy,
            "distortion_detected": S0.strip() != S3.strip()
        }
    
    def _inject_inversion(self, mos_string: str) -> str:
        """Apply orientation inversion for C→A edge"""
        # Swap 🔴 and ⚪ coordinates
        inverted = mos_string.replace('🔴', 'X').replace('⚪', '🔴').replace('X', '⚪')
        # Add explicit twist indicator
        return inverted + " 🔺"
    
    def _calculate_holonomy(self, start: str, end: str) -> Dict:
        """Measure dimensional curvature signature"""
        s_parsed = MobiusOperatorString(start)
        e_parsed = MobiusOperatorString(end)
        
        return {
            "vertex_shift": len(s_parsed.vertices) - len(e_parsed.vertices),
            "twist_delta": e_parsed.twist_count - s_parsed.twist_count,
            "flip_introduced": e_parsed.detect_coordinate_flip() and not s_parsed.detect_coordinate_flip(),
            "edit_distance": sum(1 for a, b in zip(start, end) if a != b)
        }


# Canonical base object O₀
CANONICAL_MOS = "🔴1️⃣⚪0️⃣🟡0️⃣ ▶️ ⏭️ 🔴0️⃣⚪1️⃣🟡0️⃣ ▶️ 🔺 ⏭️ 🔴0️⃣⚪0️⃣🟡1️⃣ ⏭️"
"""
O₀ = Möbius-Penrose triangle baseline object
3 vertices, single ½ twist, closed loop
"""
