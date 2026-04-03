"""
Example usage of Nych subsystem
"""

from nych import Nych, NychContext
from nych.nych import ModalityType


def basic_example():
    """Basic processing example"""
    print("=== Nych Basic Example ===")
    
    # Initialize Nych subsystem at root level
    nych = Nych()
    
    # Test with "football" - demonstrates elliptical shape matching
    result = nych.process("football")
    print(f"\nInput: football")
    print(f"Emoji: {result.emoji}")
    print(f"Phonetic signature: {result.phonetic_signature}")
    print(f"Modality: {result.modality_match.name}")
    print(f"Gestalt score: {result.gestalt_score:.3f}")
    print(f"Features: {result.metadata['gestalt_features']}")
    
    # Test with invariant word
    result = nych.process("twist")
    print(f"\nInput: twist (invariant)")
    print(f"Emoji: {result.emoji}")
    print(f"Phonetic signature: {result.phonetic_signature}")
    print(f"Invariant applied: {result.metadata['invariant_applied']}")
    
    # Test with auditory word
    result = nych.process("listen")
    print(f"\nInput: listen")
    print(f"Emoji: {result.emoji}")
    print(f"Modality: {result.modality_match.name}")


def hierarchy_example():
    """Demonstrate hierarchical subsystem integration"""
    print("\n=== Hierarchy Example ===")
    
    # Root level subsystem
    root = Nych(NychContext(hierarchy_level=0))
    print(f"Root level: {root.context.hierarchy_level}")
    
    # Create child subsystem at level 1
    child = root.create_child()
    print(f"Child level: {child.context.hierarchy_level}")
    
    # Create grandchild subsystem at level 2
    grandchild = child.create_child()
    print(f"Grandchild level: {grandchild.context.hierarchy_level}")
    
    # Process at different hierarchy levels
    result_root = root.process("ball")
    result_child = child.process("ball")
    result_grandchild = grandchild.process("ball")
    
    print(f"\nRoot result score: {result_root.gestalt_score:.3f}")
    print(f"Child result score: {result_child.gestalt_score:.3f}")
    print(f"Grandchild result score: {result_grandchild.gestalt_score:.3f}")


def modalty_hint_example():
    """Demonstrate modality hinting"""
    print("\n=== Modality Hint Example ===")
    
    nych = Nych()
    
    # Force visual modality
    result_visual = nych.process("signal", ModalityType.VISUAL)
    print(f"Visual modality result: {result_visual.emoji}")
    
    # Force auditory modality
    result_auditory = nych.process("signal", ModalityType.AUDITORY)
    print(f"Auditory modality result: {result_auditory.emoji}")


def phonetic_compression_example():
    """Demonstrate phonetic compression"""
    print("\n=== Phonetic Compression Example ===")
    
    from nych.phonetic import PhoneticCompressor
    
    compressor = PhoneticCompressor()
    
    test_words = ["football", "basketball", "triangle", "rotation", "stabilize"]
    
    for word in test_words:
        compressed, metadata = compressor.compress_with_metadata(word)
        print(f"{word:12} → {compressed:8} (ratio: {metadata['compression_ratio']:.2f})")


if __name__ == "__main__":
    basic_example()
    hierarchy_example()
    modalty_hint_example()
    phonetic_compression_example()
