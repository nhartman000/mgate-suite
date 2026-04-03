"""
Test suite for 5th Order NYCH Gestalt System
"""

from nych_system import NYCHSystem

def test_invariant_mappings():
    nych = NYCHSystem()
    
    # Test invariant core mappings - these must NEVER change
    assert nych.match_gestalt("see") == ("👀", 1.0)
    assert nych.match_gestalt("look") == ("👀", 1.0)
    assert nych.match_gestalt("visual") == ("👀", 1.0)
    assert nych.match_gestalt("hear") == ("👂👂", 1.0)
    assert nych.match_gestalt("listen") == ("👂👂", 1.0)
    assert nych.match_gestalt("auditory") == ("👂👂", 1.0)
    print("✓ Invariant mappings correct")

def test_compression_algorithm():
    nych = NYCHSystem()
    
    # Vowel removal
    assert nych.compress_word("football") == "FTBL"
    assert nych.compress_word("hello") == "HL"
    assert nych.compress_word("testing") == "TSTNG"
    assert nych.compress_word("example") == "XMPL"
    assert nych.compress_word("aardvark") == "RDVRK"
    
    # Double consonant removal
    assert nych.compress_word("ball") == "BL"
    assert nych.compress_word("better") == "BTR"
    assert nych.compress_word("coffee") == "CF"
    print("✓ Compression algorithm correct")

def test_gestalt_matching():
    nych = NYCHSystem()
    
    # Exact matches
    assert nych.match_gestalt("football") == ("🏈", 0.95)
    assert nych.match_gestalt("circle") == ("⭕", 0.95)
    assert nych.match_gestalt("rocket") == ("🚀", 0.95)
    assert nych.match_gestalt("box") == ("📦", 0.95)
    
    # Fuzzy prefix matches
    emoji, conf = nych.match_gestalt("foot")
    assert emoji == "🏈"
    assert conf > 0.7
    
    emoji, conf = nych.match_gestalt("circular")
    assert emoji == "⭕"
    assert conf > 0.7
    
    # Gestalt classification fallback
    emoji, conf = nych.match_gestalt("roundthing")
    assert emoji in ["⚽", "⭕", "☀️"]
    assert conf >= 0.5
    
    print("✓ Gestalt matching correct")

def test_text_transformation():
    nych = NYCHSystem()
    
    test_text = "I see a football and hear music"
    result = nych.apply_to_text(test_text)
    
    assert "👀[S]" in result
    assert "🏈[FTBL]" in result
    assert "👂👂[HR]" in result
    assert "🎵[MSC]" in result
    
    print("✓ Text transformation correct")

def test_order_containment():
    nych = NYCHSystem()
    info = nych.get_order_info()
    
    assert info["order"] == 5
    assert info["anchor"] == -0.500003
    assert info["external_calls"] == False
    
    print("✓ Order containment invariants satisfied")

if __name__ == "__main__":
    test_invariant_mappings()
    test_compression_algorithm()
    test_gestalt_matching()
    test_text_transformation()
    test_order_containment()
    print("\n✅ All NYCH 5th Order system tests passed")
