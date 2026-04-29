from typing import Dict, Any
import re

from .base import Modality, ModalityType


class KinestheticModality(Modality):
    """
    Kinesthetic input modality
    Handles body feel, pressure, motion, force patterns
    """
    
    modality_type = ModalityType.KINESTHETIC
    
    # Kinesthetic keyword patterns
    kinesthetic_patterns = [
        r'(touch|feel|grasp|hold|grip)',
        r'(move|push|pull|lift|press)',
        r'(hard|soft|heavy|light|weight)',
        r'(fast|slow|speed|momentum|force)',
        r'(hot|cold|warm|temperature)',
        r'(balance|stable|steady|shake)'
    ]
    
    def match_score(self, word: str) -> float:
        """Calculate kinesthetic modality match score"""
        word_lower = word.lower()
        matches = sum(1 for pattern in self.kinesthetic_patterns if re.search(pattern, word_lower))
        return min(1.0, matches / len(self.kinesthetic_patterns) * 2)
    
    def get_features(self, word: str) -> Dict[str, Any]:
        """Extract kinesthetic features from word"""
        features = {
            "force_magnitude": self._detect_force(word),
            "motion_type": self._detect_motion(word),
            "pressure_hint": self._detect_pressure(word)
        }
        return features
    
    def _detect_force(self, word: str) -> str:
        word_lower = word.lower()
        if re.search(r'(heavy|strong|hard|push|pull)', word_lower):
            return "high"
        if re.search(r'(light|soft|gentle|touch)', word_lower):
            return "low"
        return "neutral"
    
    def _detect_motion(self, word: str) -> str:
        word_lower = word.lower()
        if re.search(r'(fast|quick|sudden)', word_lower):
            return "fast"
        if re.search(r'(slow|gradual|steady)', word_lower):
            return "slow"
        return "static"
    
    def _detect_pressure(self, word: str) -> str:
        word_lower = word.lower()
        if re.search(r'(press|squeeze|grip)', word_lower):
            return "high"
        if re.search(r'(touch|brush|glance)', word_lower):
            return "low"
        return "neutral"
    
    def transform(self, input_data: Any) -> Any:
        return input_data
