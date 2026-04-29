"""
Nych - 5th-order subsystem for natural language processing
Modular add-in system for Kadmon frameworks
"""

__version__ = "1.0.0"
__author__ = "Nych Team"

from .nych import Nych, NychContext, NychResult, ModalityType
from .modality import VisualModality, AuditoryModality, KinestheticModality
from .emoji.gestalt import GestaltSelector
from .phonetic.compressor import PhoneticCompressor
from .invariant.mobius import MobiusInvariant

__all__ = [
    "Nych",
    "NychContext",
    "NychResult",
    "ModalityType",
    "VisualModality",
    "AuditoryModality", 
    "KinestheticModality",
    "GestaltSelector",
    "PhoneticCompressor",
    "MobiusInvariant"
]
