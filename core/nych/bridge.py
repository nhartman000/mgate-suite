import re
import unicodedata
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# 5th Order System: NYCH Protocol
# Natural Language → Gestalt Symbolic Encoding
# Operates at any order level, zero API calls required

class Modality(Enum):
    VISUAL = "👀"
    AUDITORY = "👂"
    KINESTHETIC = "✋"
    INTERNAL = "🧠"

INVARIANT_SYMBOLS = {
    "see": Modality.VISUAL.value,
    "look": Modality.VISUAL.value,
    "watch": Modality.VISUAL.value,
    "view": Modality.VISUAL.value,
    "observe": Modality.VISUAL.value,
    "visual": Modality.VISUAL.value,
    
    "hear": Modality.AUDITORY.value,
    "listen": Modality.AUDITORY.value,
    "sound": Modality.AUDITORY.value,
    "speak": Modality.AUDITORY.value,
    "say": Modality.AUDITORY.value,
    "tell": Modality.AUDITORY.value,
    "auditory": Modality.AUDITORY.value,
    
    "feel": Modality.KINESTHETIC.value,
    "touch": Modality.KINESTHETIC.value,
    "hold": Modality.KINESTHETIC.value,
    "grasp": Modality.KINESTHETIC.value,
    "move": Modality.KINESTHETIC.value,
    "kinesthetic": Modality.KINESTHETIC.value,
    
    "think": Modality.INTERNAL.value,
    "remember": Modality.INTERNAL.value,
    "imagine": Modality.INTERNAL.value,
    "know": Modality.INTERNAL.value,
    "believe": Modality.INTERNAL.value
}

@dataclass
class GestaltMatch:
    word: str
    emoji: str
    consonants: str
    stability: float

class NYCHSystem:
    """
    5th Order System: NYCH Symbolic Encoder
    
    Insertable at any level of the Kadmon order hierarchy.
    Zero API calls required. Pure deterministic function.
    Converts natural language → emoji gestalt symbol stream.
    """
    
    def __init__(self):
        self.order_level = 5
        self.vowels = set('aeiouy')
        self.gestalt_cache: Dict[str, GestaltMatch] = {}
        
        # Core shape mapping table (gestalt shape matching)
        self.shape_map = [
            # Round / circular shapes
            (r'(ball|sphere|circle|round|globe|orb|wheel)', '⚽', 0.95),
            (r'(football|oval|ellipse)', '🏈', 0.90),
            (r'(square|box|cube|block)', '🟦', 0.90),
            (r'(triangle|pyramid|delta)', '🔺', 0.90),
            (r'(diamond|rhombus)', '💎', 0.85),
            (r'(star|asterisk)', '⭐', 0.90),
            (r'(cross|plus)', '➕', 0.85),
            
            # Linear / directional
            (r'(line|path|edge|string|wire)', '➖', 0.85),
            (r'(arrow|point|direction)', '▶️', 0.90),
            (r'(up|ascend|rise)', '⬆️', 0.85),
            (r'(down|descend|fall)', '⬇️', 0.85),
            (r'(left)', '⬅️', 0.85),
            (r'(right)', '➡️', 0.85),
            
            # Container shapes
            (r'(house|building|home)', '🏠', 0.90),
            (r'(door|entrance|gate)', '🚪', 0.85),
            (r'(window|opening)', '🪟', 0.85),
            (r'(table|surface)', '🪑', 0.80),
            (r'(chair|seat)', '🪑', 0.85),
            
            # Tools and actions
            (r'(hammer|hit|strike)', '🔨', 0.90),
            (r'(knife|cut|slice)', '🔪', 0.90),
            (r'(book|read|text)', '📖', 0.90),
            (r'(pen|write|draw)', '✏️', 0.90),
            (r'(light|bright|shine)', '💡', 0.90),
            (r'(fire|burn|hot)', '🔥', 0.90),
            (r'(water|wet|liquid)', '💧', 0.90),
            (r'(tree|plant|wood)', '🌳', 0.90),
            
            # Abstract operators
            (r'(check|verify|test)', '✅', 0.90),
            (r'(close|end|finish)', '⏭️', 0.85),
            (r'(loop|repeat|cycle)', '🔁', 0.90),
            (r'(lock|secure|fixed)', '🔒', 0.90),
            (r'(open|unlock|free)', '🔓', 0.85),
            (r'(twist|rotate|spin)', '🔄', 0.85),
            (r'(align|match|fit)', '🎯', 0.85),
        ]
    
    def extract_consonants(self, word: str) -> str:
        """Remove vowels, deduplicate, return consonant skeleton"""
        word = word.lower()
        consonants = []
        prev = None
        
        for c in word:
            if c not in self.vowels and c.isalpha():
                if c != prev:
                    consonants.append(c)
                    prev = c
        
        return ''.join(consonants).upper()
    
    def match_gestalt(self, word: str) -> GestaltMatch:
        """Match word to closest emoji by gestalt shape"""
        if word in self.gestalt_cache:
            return self.gestalt_cache[word]
        
        # Check invariant symbols first
        lower_word = word.lower()
        for keyword, emoji in INVARIANT_SYMBOLS.items():
            if keyword in lower_word:
                match = GestaltMatch(
                    word=word,
                    emoji=emoji,
                    consonants=self.extract_consonants(word),
                    stability=1.0
                )
                self.gestalt_cache[word] = match
                return match
        
        # Gestalt shape matching
        best_match = None
        best_score = 0.0
        
        for pattern, emoji, base_score in self.shape_map:
            if re.search(pattern, lower_word):
                score = base_score
                if score > best_score:
                    best_score = score
                    best_match = emoji
        
        # Fallback: use unicode character name gestalt matching
        if not best_match:
            best_match = self._unicode_gestalt_match(word)
            best_score = 0.6
        
        match = GestaltMatch(
            word=word,
            emoji=best_match,
            consonants=self.extract_consonants(word),
            stability=best_score
        )
        
        self.gestalt_cache[word] = match
        return match
    
    def _unicode_gestalt_match(self, word: str) -> str:
        """Fallback matcher using unicode character name properties"""
        try:
            first_char = word[0].lower()
            
            # Map first letter to shape categories
            if first_char in 'oqcgbp':
                return '⚪'
            elif first_char in 'aeimnruvwz':
                return '➖'
            elif first_char in 'kxy':
                return '✖'
            elif first_char in 'dth':
                return '🔺'
            elif first_char in 's$':
                return '〰️'
            else:
                return '▪️'
        except:
            return '▪️'
    
    def encode_token(self, token: str) -> Tuple[str, str]:
        """Encode single token → (emoji, consonant_metadata)"""
        match = self.match_gestalt(token)
        return (match.emoji, match.consonants)
    
    def encode_text(self, text: str) -> List[Tuple[str, str]]:
        """Encode full text → symbol stream with metadata"""
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [self.encode_token(token) for token in tokens]
    
    def encode_stream(self, text: str) -> str:
        """NYCH compressed format: emoji + embedded consonant metadata"""
        encoded = self.encode_text(text)
        stream = []
        
        for emoji, meta in encoded:
            stream.append(f"{emoji}<{meta}>")
        
        return ' '.join(stream)
    
    def extract_domain(self, text: str) -> Dict:
        """Extract Domain + Subject + Intent + Competency"""
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        domain = {
            "modality": [],
            "operators": [],
            "subject": [],
            "tote_loops": self.detect_tote_loops(text)
        }
        
        for token in tokens:
            if token in INVARIANT_SYMBOLS:
                domain["modality"].append(INVARIANT_SYMBOLS[token])
            else:
                domain["subject"].append(token)
        
        return domain
    
    def detect_tote_loops(self, text: str) -> List[str]:
        """Detect TOTE (Test-Operate-Test-Exit) loop patterns"""
        patterns = [
            (r'(check.*then|if.*then|when.*then)', "TOTE"),
            (r'(repeat|until|while)', "LOOP"),
            (r'(verify|confirm|validate)', "TEST"),
            (r'(do|execute|perform)', "OPERATE"),
            (r'(finish|done|complete)', "EXIT"),
        ]
        
        detected = []
        for pattern, loop_type in patterns:
            if re.search(pattern, text.lower()):
                detected.append(loop_type)
        
        return list(set(detected))
    
    def validate_continuity(self, stream1: str, stream2: str) -> float:
        """Validate continuity between two symbol streams"""
        sym1 = set(re.findall(r'[^<]+', stream1))
        sym2 = set(re.findall(r'[^<]+', stream2))
        
        intersection = len(sym1.intersection(sym2))
        union = len(sym1.union(sym2))
        
        return intersection / union if union > 0 else 0.0

class NYCHBridge:
    """
    Bridge to inject NYCH 5th order system into any Kadmon order level
    
    Can be attached to:
    - 1st order environment
    - 2nd order pair/couple
    - 3rd order LLM
    - 4th order MGATE
    
    Zero execution order violation - operates as pure filter.
    """
    
    def __init__(self):
        self.nych = NYCHSystem()
        self.attached_to = None
        self.order_attached = 0
    
    def attach(self, system, order_level: int):
        """Attach NYCH encoder to any order system"""
        self.attached_to = system
        self.order_attached = order_level
    
    def process_input(self, text: str) -> Dict:
        """Process natural language input at attached order level"""
        return {
            "raw_text": text,
            "symbol_stream": self.nych.encode_stream(text),
            "domain": self.nych.extract_domain(text),
            "order_processed": self.order_attached,
            "stability": sum(m.stability for m in self.nych.gestalt_cache.values()) / max(1, len(self.nych.gestalt_cache))
        }
    
    def inject_prompt_header(self, prompt: str) -> str:
        """Inject NYCH symbol stream into LLM prompt header"""
        encoded = self.nych.encode_stream(prompt)
        return f"[NYCH:{encoded}]\n\n{prompt}"
