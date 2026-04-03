#!/usr/bin/env python3
"""
Simple test script for Nych subsystem
"""

import sys
sys.path.insert(0, '.')

from nych import Nych
from nych.phonetic import PhoneticCompressor
from nych.emoji import GestaltSelector


def test_phonetic_compression():
    print("Testing phonetic compression...")
    compressor = PhoneticCompressor()
    
    test_cases = [
        ("football", "FTBL"),
        ("basketball", "BSKTBL"),
        ("triangle", "TRNGL"),
        ("rotation", "RTTN"),
        ("stabilize", "STBLZ"),
        ("hello", "HLL"),
    ]
    
    all_passed = True
    for word, expected in test_cases:
        result = compressor.compress(word)
        passed = result == expected
        all_passed &= passed
        print(f"  {word:12} -> {result:8} {'OK' if passed else f'FAIL (expected {expected})'}")
    
    return all_passed


def test_gestalt_selector():
    print("\nTesting gestalt selector...")
    selector = GestaltSelector()
    
    test_cases = [
        ("football", ["⚽", "🏈"]),
        ("circle", ["⭕", "🔵", "🔴"]),
        ("triangle", ["🔺"]),
        ("moon", ["🌙"]),
    ]
    
    all_passed = True
    for word, expected_emojis in test_cases:
        result = selector.find_closest(word)
        passed = result.emoji in expected_emojis
        all_passed &= passed
        print(f"  {word:12} → {result.emoji} (score: {result.score:.3f}) {'✓' if passed else '✗'}")
    
    return all_passed


def test_modality_detection():
    print("\nTesting modality detection...")
    nych = Nych()
    
    test_cases = [
        ("look", "VISUAL"),
        ("listen", "AUDITORY"),
        ("touch", "KINESTHETIC"),
        ("bright", "VISUAL"),
        ("loud", "AUDITORY"),
        ("heavy", "KINESTHETIC"),
    ]
    
    all_passed = True
    for word, expected_modality in test_cases:
        result = nych.process(word)
        passed = result.modality_match.name == expected_modality
        all_passed &= passed
        print(f"  {word:12} → {result.modality_match.name:12} {'✓' if passed else f'✗ (expected {expected_modality})'}")
    
    return all_passed


def test_invariants():
    print("\nTesting invariants...")
    nych = Nych()
    
    test_cases = [
        ("twist", True),
        ("flip", True),
        ("align", True),
        ("randomword", False),
    ]
    
    all_passed = True
    for word, expected in test_cases:
        result = nych.process(word)
        passed = result.metadata["invariant_applied"] == expected
        all_passed &= passed
        print(f"  {word:12} → invariant={result.metadata['invariant_applied']} {'✓' if passed else f'✗ (expected {expected})'}")
    
    return all_passed


def main():
    print("=== Nych Subsystem Tests ===\n")
    
    tests = [
        test_phonetic_compression,
        test_gestalt_selector,
        test_modality_detection,
        test_invariants
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Results: {passed}/{len(tests)} tests passed ===")
    
    if passed == len(tests):
        print("\n✅ All tests passed! Nych subsystem is working correctly.")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
