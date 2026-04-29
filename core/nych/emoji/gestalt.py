from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re


@dataclass
class EmojiMatch:
    """Result container for gestalt emoji matching"""
    emoji: str
    word: str
    score: float
    features: Dict[str, float]


@dataclass
class EmojiEntry:
    emoji: str
    keywords: List[str]
    shape_features: Dict[str, float]
    conceptual_tags: List[str]


class GestaltSelector:
    """
    Offline emoji gestalt selector
    Performs real-time matching without API dependencies
    Prioritizes shape, form, and conceptual similarity
    """
    
    def __init__(self):
        self.emoji_database = self._build_database()
        self.feature_weights = {
            "shape": 0.4,
            "form": 0.3,
            "conceptual": 0.2,
            "keyword": 0.1
        }
    
    def _build_database(self) -> List[EmojiEntry]:
        """Build offline emoji database with gestalt features"""
        return [
            # Sports & Objects
            EmojiEntry("⚽", ["football", "soccer", "ball"], 
                      {"circular": 0.9, "elliptical": 0.3, "spherical": 0.9}, 
                      ["round", "sport", "game"]),
            EmojiEntry("🏈", ["football", "american", "oval"], 
                      {"circular": 0.2, "elliptical": 0.9, "pointed": 0.8}, 
                      ["sport", "game", "oval"]),
            EmojiEntry("⚾", ["baseball", "ball"], 
                      {"circular": 0.9, "spherical": 0.9}, 
                      ["round", "sport", "game"]),
            EmojiEntry("🏀", ["basketball", "ball"], 
                      {"circular": 0.9, "spherical": 0.9}, 
                      ["round", "sport", "game"]),
            EmojiEntry("🎾", ["tennis", "ball"], 
                      {"circular": 0.9, "spherical": 0.9}, 
                      ["round", "sport", "game"]),
            
            # Shapes
            EmojiEntry("⭕", ["circle", "round", "ball"], 
                      {"circular": 1.0, "spherical": 0.5}, 
                      ["shape", "round", "empty"]),
            EmojiEntry("🔵", ["circle", "round", "blue"], 
                      {"circular": 1.0, "spherical": 0.7}, 
                      ["shape", "round", "solid"]),
            EmojiEntry("🔴", ["circle", "round", "red"], 
                      {"circular": 1.0, "spherical": 0.7}, 
                      ["shape", "round", "solid"]),
            EmojiEntry("⬜", ["square", "box"], 
                      {"rectangular": 1.0, "flat": 0.9}, 
                      ["shape", "square"]),
            EmojiEntry("🔺", ["triangle", "pointed"], 
                      {"triangular": 1.0, "pointed": 0.9}, 
                      ["shape", "triangle", "up"]),
            
            # Natural forms
            EmojiEntry("🌙", ["moon", "crescent", "curve"], 
                      {"curved": 0.9, "elliptical": 0.5, "pointed": 0.3}, 
                      ["night", "shape", "curve"]),
            EmojiEntry("☀️", ["sun", "star", "round"], 
                      {"circular": 0.9, "pointed": 0.4}, 
                      ["light", "day", "round"]),
            EmojiEntry("⭐", ["star", "pointed"], 
                      {"pointed": 0.9, "symmetric": 0.8}, 
                      ["light", "shape", "pointed"]),
            
            # Animals
            EmojiEntry("🐶", ["dog", "pet"], 
                      {"organic": 0.9, "quadruped": 0.8}, 
                      ["animal", "pet", "friendly"]),
            EmojiEntry("🐱", ["cat", "pet"], 
                      {"organic": 0.9, "quadruped": 0.8}, 
                      ["animal", "pet", "independent"]),
            
            # Actions
            EmojiEntry("👀", ["eye", "look", "see"], 
                      {"circular": 0.7, "organic": 0.6}, 
                      ["visual", "watch", "attention"]),
            EmojiEntry("👂", ["ear", "hear", "listen"], 
                      {"curved": 0.6, "organic": 0.7}, 
                      ["auditory", "listen", "attention"]),
            EmojiEntry("✋", ["hand", "stop", "five"], 
                      {"organic": 0.8, "spread": 0.7}, 
                      ["kinesthetic", "touch", "gesture"]),
        ]
    
    def find_closest(self, word: str) -> EmojiMatch:
        """
        Find closest emoji based on gestalt principles
        
        Args:
            word: Input word to match
            
        Returns:
            EmojiMatch with best matching emoji and score
        """
        word_lower = word.lower()
        word_features = self._extract_word_features(word_lower)
        
        best_score = -1.0
        best_match = None
        best_features = {}
        
        for entry in self.emoji_database:
            score, features = self._calculate_similarity(word_lower, word_features, entry)
            
            if score > best_score:
                best_score = score
                best_match = entry
                best_features = features
        
        if not best_match:
            return EmojiMatch("❓", word, 0.0, {})
        
        return EmojiMatch(
            emoji=best_match.emoji,
            word=word,
            score=best_score,
            features=best_features
        )
    
    def _extract_word_features(self, word: str) -> Dict[str, float]:
        """Extract gestalt features from input word"""
        features = {}
        
        # Shape inference from word patterns
        if re.search(r'(ball|circle|round|sphere|orb)', word):
            features["circular"] = 0.9
            features["spherical"] = 0.8
        if re.search(r'(oval|ellipse|football)', word):
            features["elliptical"] = 0.9
            features["pointed"] = 0.7
        if re.search(r'(square|box|cube|rectangle)', word):
            features["rectangular"] = 0.9
            features["flat"] = 0.6
        if re.search(r'(triangle|point|pyramid|sharp)', word):
            features["triangular"] = 0.9
            features["pointed"] = 0.9
        if re.search(r'(curve|arc|bend|moon)', word):
            features["curved"] = 0.9
        if re.search(r'(star|asterisk)', word):
            features["pointed"] = 0.9
            features["symmetric"] = 0.8
        
        return features
    
    def _calculate_similarity(self, word: str, word_features: Dict[str, float], 
                             entry: EmojiEntry) -> Tuple[float, Dict[str, float]]:
        """Calculate gestalt similarity score between word and emoji entry"""
        scores = {}
        
        # Keyword match score
        keyword_score = 1.0 if word in entry.keywords else 0.0
        if not keyword_score:
            keyword_score = max(0.0, 1.0 - min(1.0, 
                min(len(set(word).symmetric_difference(set(k))) / 10 
                    for k in entry.keywords)))
        scores["keyword"] = keyword_score
        
        # Shape similarity
        shape_overlap = 0.0
        common_features = set(word_features.keys()) & set(entry.shape_features.keys())
        if common_features:
            shape_overlap = sum(
                abs(word_features[f] - entry.shape_features[f]) 
                for f in common_features
            ) / len(common_features)
            shape_overlap = 1.0 - shape_overlap
        scores["shape"] = shape_overlap
        
        # Form similarity
        form_score = 0.0
        for tag in entry.conceptual_tags:
            if tag in word:
                form_score += 0.25
        scores["form"] = min(1.0, form_score)
        
        # Conceptual similarity
        conceptual_score = 0.0
        word_chars = set(word)
        for kw in entry.keywords:
            conceptual_score = max(conceptual_score,
                len(word_chars & set(kw)) / max(len(word), len(kw)))
        scores["conceptual"] = conceptual_score
        
        # Weighted total score
        total_score = sum(
            scores[feature] * weight 
            for feature, weight in self.feature_weights.items()
        )
        
        return total_score, scores
    
    def find_all(self, word: str, limit: int = 5) -> List[EmojiMatch]:
        """Find top N matching emojis"""
        word_lower = word.lower()
        word_features = self._extract_word_features(word_lower)
        
        results = []
        for entry in self.emoji_database:
            score, features = self._calculate_similarity(word_lower, word_features, entry)
            results.append(EmojiMatch(entry.emoji, word, score, features))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
