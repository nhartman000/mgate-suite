from typing import Dict, Any
import re

from .base import Modality, ModalityType


class AuditoryModality(Modality):
    """
    External auditory input modality
    Handles sound, tone, speech, timing patterns
    """
    
    modality_type = ModalityType.AUDITORY
    
    # Auditory keyword patterns
    auditory_patterns = [
        r'(sound|hear|listen|noise|tone|pitch)',
        r'(speak|say|talk|word|voice|pronounce)',
        r'(loud|quiet|soft|volume)',
        r'(fast|slow|tempo|rhythm|beat)',
        r'(ring|buzz|hum|whistle|sing)',
        r'(echo|reverb|silent|quiet)'
    ]
    
    def match_score(self, word: str) -> float:
        """Calculate auditory modality match score"""
        word_lower = word.lower()
        matches = sum(1 for pattern in self.auditory_patterns if re.search(pattern, word_lower))
        return min(1.0, matches / len(self.auditory_patterns) * 2)
    
    def get_features(self, word: str) -> Dict[str, Any]:
        """Extract auditory features from word"""
        features = {
            "phonetic_length": len(word),
            "vowel_count": self._count_vowels(word),
            "consonant_count": self._count_consonants(word),
            "syllable_estimate": self._estimate_syllables(word)
        }
        return features
    
    def _count_vowels(self, word: str) -> int:
        vowels = set('aeiouyAEIOUY')
        return sum(1 for c in word if c in vowels)
    
    def _count_consonants(self, word: str) -> int:
        consonants = set('bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ')
        return sum(1 for c in word if c in consonants)
    
    def _estimate_syllables(self, word: str) -> int:
        word_lower = word.lower()
        count = 0
        vowels = "aeiouy"
        prev_char_was_vowel = False
        
        for char in word_lower:
            is_vowel = char in vowels
            if is_vowel and not prev_char_was_vowel:
                count += 1
            prev_char_was_vowel = is_vowel
        
        if word_lower.endswith('e'):
            count = max(1, count - 1)
            
        return max(1, count)
    
    def transform(self, input_data: Any) -> Any:
        return input_data
