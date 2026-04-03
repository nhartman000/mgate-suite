"""
5th Order NYCH System
Natural Language Gestalt Emoji Mapper
Add-in module compatible with all Kadmon system orders

Order Position: 5th Order (contained within 4th Order MGATE/MCP)
Invariant Anchor: -0.500003
Zero external API calls. Pure gestalt matching.
"""

import re
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class NYCHToken:
    original: str
    emoji: str
    compressed: str
    domain: Optional[str] = None
    confidence: float = 1.0

class NYCHSystem:
    """
    5th Order NYCH Natural Language Gestalt System
    
    Invariants:
    - 👀 = visual external input (fixed invariant)
    - 👂👂 = auditory external input (fixed invariant)
    - All other words matched by gestalt shape
    - No external API calls
    - Compression removes vowels + doubles
    """
    
    # INVARIANT CORE MAPPINGS - THESE CANNOT BE CHANGED
    _INVARIANT_MAPPINGS = {
        "see": "👀",
        "look": "👀",
        "watch": "👀",
        "visual": "👀",
        "eye": "👀",
        "view": "👀",
        "observe": "👀",
        "see": "👀",
        "hear": "👂👂",
        "listen": "👂👂",
        "sound": "👂👂",
        "auditory": "👂👂",
        "ear": "👂👂",
        "speak": "👄",
        "say": "👄",
        "talk": "👄",
        "mouth": "👄",
        "touch": "✋",
        "feel": "✋",
        "hand": "✋",
        "smell": "👃",
        "nose": "👃",
        "think": "🧠",
        "mind": "🧠",
        "brain": "🧠",
        "know": "🧠",
    }
    
    # GESTALT SHAPE MAPPINGS - matched by form/silhouette
    _GESTALT_MAPPINGS = {
        # Circular / Round
        "ball": "⚽",
        "sphere": "⚽",
        "circle": "⭕",
        "round": "⭕",
        "sun": "☀️",
        "moon": "🌙",
        "earth": "🌍",
        "world": "🌍",
        "coin": "🪙",
        "wheel": "⚙️",
        
        # Pointed / Elliptical
        "football": "🏈",
        "oval": "🏈",
        "egg": "🥚",
        "rocket": "🚀",
        "arrow": "➡️",
        "point": "📍",
        "needle": "📍",
        "spear": "🔱",
        "diamond": "💎",
        
        # Linear / Horizontal
        "line": "➖",
        "road": "🛣️",
        "path": "🛤️",
        "stick": "🥢",
        "bar": "➖",
        "horizontal": "➖",
        
        # Vertical
        "tower": "🗼",
        "building": "🏢",
        "tree": "🌲",
        "pole": "🎣",
        "column": "🏛️",
        "up": "⬆️",
        "down": "⬇️",
        
        # Angular / Square
        "box": "📦",
        "square": "⬜",
        "cube": "🧊",
        "block": "🧱",
        "house": "🏠",
        "window": "🪟",
        "door": "🚪",
        
        # Complex forms
        "person": "🧑",
        "human": "🧑",
        "man": "👨",
        "woman": "👩",
        "child": "👶",
        "group": "👥",
        "crowd": "👥",
        "animal": "🐾",
        "dog": "🐕",
        "cat": "🐈",
        "bird": "🐦",
        "fish": "🐟",
        "car": "🚗",
        "vehicle": "🚗",
        "boat": "🚢",
        "plane": "✈️",
        "time": "⏰",
        "clock": "⏰",
        "day": "📅",
        "night": "🌙",
        "book": "📖",
        "paper": "📄",
        "write": "✍️",
        "food": "🍽️",
        "eat": "🍽️",
        "drink": "🥤",
        "water": "💧",
        "fire": "🔥",
        "air": "💨",
        "earth": "🪨",
        "love": "❤️",
        "heart": "❤️",
        "star": "⭐",
        "light": "💡",
        "dark": "🌑",
        "number": "🔢",
        "money": "💰",
        "work": "💼",
        "play": "🎮",
        "game": "🎮",
        "music": "🎵",
        "song": "🎵",
        "phone": "📱",
        "computer": "💻",
        "mail": "📧",
        "message": "💬",
        "question": "❓",
        "answer": "✅",
        "yes": "✅",
        "no": "❌",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅",
        "lock": "🔒",
        "key": "🔑",
        "map": "🗺️",
        "location": "📍",
        "home": "🏠",
        "sleep": "😴",
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "surprise": "😮",
        "fear": "😨",
    }
    
    # Gestalt similarity weights for fallback matching
    _GESTALT_FEATURES = {
        "round": ["⚽", "⭕", "☀️", "🌙", "🪙", "⚙️"],
        "pointed": ["🏈", "🥚", "🚀", "➡️", "📍", "🔱", "💎"],
        "square": ["📦", "⬜", "🧊", "🧱", "🏠", "🪟", "🚪"],
        "vertical": ["🗼", "🏢", "🌲", "🎣", "🏛️", "⬆️"],
        "horizontal": ["➖", "🛣️", "🛤️", "🥢"],
        "organic": ["🌲", "🐾", "🐕", "🐈", "🐦", "🐟", "🌙"],
        "manmade": ["🏢", "🚗", "✈️", "💻", "📱", "⚙️"],
    }
    
    _VOWELS = {'a', 'e', 'i', 'o', 'u', 'y'}
    
    def __init__(self):
        self.center_anchor = -0.500003
        self.order_level = 5
        
    def compress_word(self, word: str) -> str:
        """
        Remove vowels, drop double consonants, return compressed token
        """
        word = word.lower().strip()
        if not word:
            return ""
            
        # Remove vowels
        chars = [c for c in word if c not in self._VOWELS]
        
        # Remove consecutive duplicates
        compressed = []
        prev = None
        for c in chars:
            if c != prev:
                compressed.append(c)
                prev = c
                
        return ''.join(compressed).upper()
    
    def match_gestalt(self, word: str) -> Tuple[str, float]:
        """
        Match any word to closest emoji by gestalt form.
        Returns (emoji, confidence)
        Zero external API calls.
        """
        word = word.lower().strip()
        
        # First check invariant mappings - these always win
        if word in self._INVARIANT_MAPPINGS:
            return (self._INVARIANT_MAPPINGS[word], 1.0)
            
        # Exact gestalt match
        if word in self._GESTALT_MAPPINGS:
            return (self._GESTALT_MAPPINGS[word], 0.95)
            
        # Fuzzy prefix match
        for key in self._GESTALT_MAPPINGS:
            if word.startswith(key) or key.startswith(word):
                overlap = len(set(word) & set(key)) / len(set(word) | set(key))
                if overlap > 0.6:
                    return (self._GESTALT_MAPPINGS[key], 0.7 + (overlap * 0.2))
        
        # Gestalt feature classification fallback
        features = self._classify_gestalt(word)
        for feature in features:
            if feature in self._GESTALT_FEATURES and self._GESTALT_FEATURES[feature]:
                return (self._GESTALT_FEATURES[feature][0], 0.5)
                
        # Fallback default
        return ("❓", 0.2)
        
    def _classify_gestalt(self, word: str) -> List[str]:
        """Classify word by gestalt feature hints"""
        features = []
        
        # Semantic feature hints
        if any(s in word for s in ["round", "circl", "ball", "sphere", "glob"]):
            features.append("round")
        if any(s in word for s in ["point", "sharp", "oval", "egg", "arrow"]):
            features.append("pointed")
        if any(s in word for s in ["box", "squar", "cube", "block"]):
            features.append("square")
        if any(s in word for s in ["tall", "high", "tower", "up"]):
            features.append("vertical")
        if any(s in word for s in ["long", "flat", "line", "road"]):
            features.append("horizontal")
        if any(s in word for s in ["tree", "plant", "animal", "nature"]):
            features.append("organic")
        if any(s in word for s in ["build", "machin", "tech", "metal"]):
            features.append("manmade")
            
        return features
    
    def tokenize(self, text: str) -> List[NYCHToken]:
        """
        Convert natural language text into NYCH gestalt tokens
        """
        words = re.findall(r'\b\w+\b', text.lower())
        tokens = []
        
        for word in words:
            emoji, confidence = self.match_gestalt(word)
            compressed = self.compress_word(word)
            tokens.append(NYCHToken(
                original=word,
                emoji=emoji,
                compressed=compressed,
                confidence=confidence
            ))
            
        return tokens
    
    def apply_to_text(self, text: str) -> str:
        """
        Apply NYCH mapping inline to natural language text
        """
        tokens = self.tokenize(text)
        result = text
        
        for token in reversed(tokens):  # process long words first
            result = re.sub(
                rf'\b{re.escape(token.original)}\b',
                f"{token.emoji}[{token.compressed}]",
                result,
                flags=re.IGNORECASE
            )
            
        return result
    
    def get_order_info(self) -> Dict:
        """Return system order metadata for Kadmon containment validation"""
        return {
            "order": 5,
            "name": "NYCH",
            "anchor": self.center_anchor,
            "type": "gestalt_mapper",
            "external_calls": False
        }
