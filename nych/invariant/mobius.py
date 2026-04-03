from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class InvariantEntry:
    id: str
    word: str
    emoji: str
    signature: str
    twist_count: float
    modality: str


class MobiusInvariant:
    """
    Mobius invariant subsystem
    Implements discrete invariant choices from referenced Mobius document
    """
    
    def __init__(self):
        self.invariants = self._load_invariants()
        self.twist_states = {}
        
    def _load_invariants(self) -> Dict[str, InvariantEntry]:
        """Load system invariants from Mobius specification"""
        return {
            # Core topological invariants
            "twist": InvariantEntry(
                id="inv_001",
                word="twist",
                emoji="🔺",
                signature="TWST",
                twist_count=0.5,
                modality="geometric"
            ),
            "flip": InvariantEntry(
                id="inv_002",
                word="flip",
                emoji="🔺",
                signature="FLP",
                twist_count=0.5,
                modality="geometric"
            ),
            "rotate": InvariantEntry(
                id="inv_003", 
                word="rotate",
                emoji="🔄",
                signature="RTT",
                twist_count=1.0,
                modality="geometric"
            ),
            
            # Operator invariants
            "align": InvariantEntry(
                id="inv_004",
                word="align",
                emoji="▶️",
                signature="ALGN",
                twist_count=0.0,
                modality="operator"
            ),
            "check": InvariantEntry(
                id="inv_005",
                word="check",
                emoji="✅",
                signature="CHK",
                twist_count=0.0,
                modality="operator"
            ),
            "shift": InvariantEntry(
                id="inv_006",
                word="shift",
                emoji="⏩",
                signature="SHFT",
                twist_count=0.5,
                modality="operator"
            ),
            "stabilize": InvariantEntry(
                id="inv_007",
                word="stabilize",
                emoji="⏸️",
                signature="STBL",
                twist_count=0.0,
                modality="operator"
            ),
            
            # Modality invariants
            "visual": InvariantEntry(
                id="inv_008",
                word="visual",
                emoji="👀",
                signature="VS",
                twist_count=0.0,
                modality="sensory"
            ),
            "auditory": InvariantEntry(
                id="inv_009",
                word="auditory",
                emoji="👂",
                signature="AUD",
                twist_count=0.0,
                modality="sensory"
            ),
            "kinesthetic": InvariantEntry(
                id="inv_010",
                word="kinesthetic",
                emoji="✋",
                signature="KNS",
                twist_count=0.0,
                modality="sensory"
            ),
            
            # Topological markers
            "closure": InvariantEntry(
                id="inv_011",
                word="closure",
                emoji="⏭️",
                signature="CLSR",
                twist_count=1.5,
                modality="topological"
            ),
            "vertex": InvariantEntry(
                id="inv_012",
                word="vertex",
                emoji="🔴",
                signature="VTX",
                twist_count=0.0,
                modality="topological"
            ),
            "edge": InvariantEntry(
                id="inv_013",
                word="edge",
                emoji="▶️",
                signature="EDG",
                twist_count=0.0,
                modality="topological"
            ),
            
            # Frequency invariant
            "frequency": InvariantEntry(
                id="inv_014",
                word="frequency",
                emoji="〰️",
                signature="FRQ",
                twist_count=0.0,
                modality="carrier"
            )
        }
    
    def is_invariant(self, word: str) -> bool:
        """Check if word matches a system invariant"""
        return word.lower() in self.invariants
    
    def get_invariant(self, word: str) -> Optional[Dict[str, Any]]:
        """Get invariant data for word"""
        entry = self.invariants.get(word.lower())
        if not entry:
            return None
        
        return {
            "id": entry.id,
            "emoji": entry.emoji,
            "signature": entry.signature,
            "twist_count": entry.twist_count,
            "modality": entry.modality
        }
    
    def encode_result(self, emoji_result: Any, phonetic_sig: str) -> None:
        """Apply Mobius invariant encoding to result"""
        if not hasattr(emoji_result, 'metadata'):
            emoji_result.metadata = {}
        
        emoji_result.metadata.update({
            "invariant_encoding": True,
            "frequency_carrier": True,
            "twist_embedding": self._calculate_twist_embedding(phonetic_sig)
        })
    
    def _calculate_twist_embedding(self, signature: str) -> float:
        """Calculate twist embedding from phonetic signature"""
        # Each character contributes 0.5 twist potential
        base_twist = len(signature) * 0.125
        
        # Odd length adds half-twist invariant
        if len(signature) % 2 == 1:
            base_twist += 0.5
            
        return base_twist
    
    def verify_invariance(self, input_data: Any, output_data: Any) -> bool:
        """Verify that invariants were preserved through transformation"""
        # Frequency invariant check - constant modulation
        if isinstance(input_data, str) and isinstance(output_data, str):
            input_len = len([c for c in input_data if c not in "aeiouyAEIOUY"])
            output_len = len(output_data)
            ratio = output_len / input_len if input_len > 0 else 0
            
            # Invariant holds if compression ratio is consistent
            return 0.3 <= ratio <= 0.7
            
        return True
    
    def get_twist_count(self, operation: str) -> float:
        """Get required twist count for operation"""
        entry = self.invariants.get(operation.lower())
        return entry.twist_count if entry else 0.0
    
    def list_invariants(self) -> List[Dict[str, Any]]:
        """List all available system invariants"""
        return [
            {
                "word": k,
                "emoji": v.emoji,
                "twist_count": v.twist_count,
                "modality": v.modality
            }
            for k, v in self.invariants.items()
        ]
