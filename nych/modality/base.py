from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum


class ModalityType(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"


class Modality(ABC):
    """Abstract base class for sensory modalities"""
    
    modality_type: ModalityType
    
    @abstractmethod
    def match_score(self, word: str) -> float:
        """Return match score 0.0-1.0 for input word"""
        pass
    
    @abstractmethod
    def get_features(self, word: str) -> Dict[str, Any]:
        """Extract modality-specific features from word"""
        pass
    
    @abstractmethod
    def transform(self, input_data: Any) -> Any:
        """Transform input according to modality rules"""
        pass
