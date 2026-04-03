from typing import Dict, Any
import re

from .base import Modality, ModalityType


class VisualModality(Modality):
    """
    External visual input modality
    Handles shape, form, color, spatial patterns
    """
    
    modality_type = ModalityType.VISUAL
    
    # Visual keyword patterns
    visual_patterns = [
        r'(ball|circle|square|triangle|shape|form)',
        r'(see|look|view|image|picture|photo)',
        r'(color|red|blue|green|yellow|black|white)',
        r'(bright|dark|light|shadow)',
        r'(big|small|large|tiny|size)',
        r'(round|flat|curved|straight|pointed|elliptical)'
    ]
    
    def match_score(self, word: str) -> float:
        """Calculate visual modality match score"""
        word_lower = word.lower()
        matches = sum(1 for pattern in self.visual_patterns if re.search(pattern, word_lower))
        return min(1.0, matches / len(self.visual_patterns) * 2)
    
    def get_features(self, word: str) -> Dict[str, Any]:
        """Extract visual features from word"""
        features = {
            "shape": self._detect_shape(word),
            "form_complexity": self._form_complexity(word),
            "spatial_hint": self._spatial_hint(word)
        }
        return features
    
    def _detect_shape(self, word: str) -> str:
        word_lower = word.lower()
        if re.search(r'(ball|circle|round|sphere)', word_lower):
            return "circular"
        if re.search(r'(square|box|cube)', word_lower):
            return "rectangular"
        if re.search(r'(triangle|pointed|pyramid)', word_lower):
            return "triangular"
        if re.search(r'(elliptical|oval|football)', word_lower):
            return "elliptical"
        return "unknown"
    
    def _form_complexity(self, word: str) -> int:
        return min(5, len(word) // 2)
    
    def _spatial_hint(self, word: str) -> str:
        word_lower = word.lower()
        if re.search(r'(up|above|top)', word_lower):
            return "upper"
        if re.search(r'(down|below|bottom)', word_lower):
            return "lower"
        return "neutral"
    
    def transform(self, input_data: Any) -> Any:
        return input_data
