"""
Nych core subsystem implementation
5th-order subsystem integrable at any Kadmon framework level
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from .modality import Modality, VisualModality, AuditoryModality, KinestheticModality
from .emoji.gestalt import GestaltSelector
from .phonetic.compressor import PhoneticCompressor
from .invariant.mobius import MobiusInvariant


class ModalityType(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"


@dataclass
class NychContext:
    """Execution context for Nych subsystem"""
    hierarchy_level: int = 0
    parent_context: Optional['NychContext'] = None
    invariants: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NychResult:
    """Result container for Nych operations"""
    emoji: str
    phonetic_signature: str
    modality_match: ModalityType
    gestalt_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class Nych:
    """
    Nych 5th-order subsystem core
    
    Operates on discrete invariant choices across sensory modalities
    Integrable at any hierarchical level within Kadmon frameworks
    """
    
    def __init__(self, context: Optional[NychContext] = None):
        self.context = context or NychContext()
        self.modalities: Dict[ModalityType, Modality] = {
            ModalityType.VISUAL: VisualModality(),
            ModalityType.AUDITORY: AuditoryModality(),
            ModalityType.KINESTHETIC: KinestheticModality()
        }
        self.gestalt_selector = GestaltSelector()
        self.phonetic_compressor = PhoneticCompressor()
        self.mobius_invariant = MobiusInvariant()
        
        # Register subsystem with parent context if available
        if self.context.parent_context:
            self._register_with_parent()
    
    def _register_with_parent(self) -> None:
        """Register this subsystem instance at current hierarchy level"""
        if not hasattr(self.context.parent_context, 'subsystems'):
            self.context.parent_context.subsystems = []
        self.context.parent_context.subsystems.append(self)
    
    def process(self, word: str, modality_hint: Optional[ModalityType] = None) -> NychResult:
        """
        Process input word through full Nych pipeline
        
        Args:
            word: Input word to process
            modality_hint: Optional preferred modality
            
        Returns:
            NychResult with emoji, phonetic signature, and metadata
        """
        # Step 1: Detect modality or use hint
        if modality_hint:
            modality = self.modalities[modality_hint]
        else:
            modality = self._detect_modality(word)
        
        # Step 2: Check for invariant matches
        if self.mobius_invariant.is_invariant(word):
            return self._process_invariant(word, modality)
        
        # Step 3: Non-invariant path - gestalt emoji selection
        emoji_result = self.gestalt_selector.find_closest(word)
        
        # Step 4: Phonetic compression
        phonetic_sig = self.phonetic_compressor.compress(word)
        
        # Step 5: Embed phonetic signature as metadata
        emoji_with_metadata = self._embed_metadata(emoji_result.emoji, phonetic_sig)
        
        # Step 6: Apply Mobius invariant encoding
        self.mobius_invariant.encode_result(emoji_result, phonetic_sig)
        
        return NychResult(
            emoji=emoji_with_metadata,
            phonetic_signature=phonetic_sig,
            modality_match=modality.modality_type,
            gestalt_score=emoji_result.score,
            metadata={
                "gestalt_features": emoji_result.features,
                "invariant_applied": False,
                "hierarchy_level": self.context.hierarchy_level
            }
        )
    
    def _detect_modality(self, word: str) -> Modality:
        """Auto-detect most appropriate sensory modality for input"""
        scores = {
            mt: mod.match_score(word) 
            for mt, mod in self.modalities.items()
        }
        best_modality = max(scores.items(), key=lambda x: x[1])[0]
        return self.modalities[best_modality]
    
    def _process_invariant(self, word: str, modality: Modality) -> NychResult:
        """Process words that match system invariants"""
        invariant_data = self.mobius_invariant.get_invariant(word)
        
        return NychResult(
            emoji=invariant_data["emoji"],
            phonetic_signature=invariant_data["signature"],
            modality_match=modality.modality_type,
            gestalt_score=1.0,
            metadata={
                "invariant_applied": True,
                "invariant_id": invariant_data["id"],
                "hierarchy_level": self.context.hierarchy_level
            }
        )
    
    def _embed_metadata(self, emoji: str, phonetic_sig: str) -> str:
        """Embed compressed phonetic string as metadata within emoji"""
        # Zero-width joiner embedding for metadata encoding
        zwj = "\u200D"
        encoded_sig = ''.join(f"{zwj}{c}" for c in phonetic_sig)
        return f"{emoji}{encoded_sig}"
    
    def create_child(self) -> 'Nych':
        """Create child subsystem instance at next hierarchy level"""
        child_context = NychContext(
            hierarchy_level=self.context.hierarchy_level + 1,
            parent_context=self.context
        )
        return Nych(context=child_context)
    
    def apply_operator(self, operator_name: str, input_data: Any) -> Any:
        """Apply Nych primitive operator"""
        operators = {
            "align": self._op_align,
            "check": self._op_check,
            "shift": self._op_shift,
            "amplify": self._op_amplify,
            "interrupt": self._op_interrupt,
            "stabilize": self._op_stabilize
        }
        
        if operator_name not in operators:
            raise ValueError(f"Unknown operator: {operator_name}")
            
        return operators[operator_name](input_data)
    
    def _op_align(self, data: Any) -> Any: return data
    def _op_check(self, data: Any) -> Any: return data
    def _op_shift(self, data: Any) -> Any: return data
    def _op_amplify(self, data: Any) -> Any: return data
    def _op_interrupt(self, data: Any) -> Any: return data
    def _op_stabilize(self, data: Any) -> Any: return data
