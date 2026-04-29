from typing import Set


class PhoneticCompressor:
    """
    Phonetic compression system
    Removes vowels, eliminates double consonants
    Embeds compressed string as emoji metadata
    """
    
    def __init__(self):
        self.vowels: Set[str] = {'a', 'e', 'i', 'o', 'u', 'y', 'A', 'E', 'I', 'O', 'U', 'Y'}
    
    def compress(self, word: str) -> str:
        """
        Compress word using phonetic rules:
        1. Remove all vowels
        2. Eliminate double consonants
        3. Convert to uppercase
        
        Args:
            word: Input word to compress
            
        Returns:
            Compressed consonant string
        """
        # Step 1: Remove all vowels
        consonants = [c for c in word if c not in self.vowels]
        
        # Step 2: Remove double consonants (keep one instance)
        compressed = []
        prev_char = None
        
        for char in consonants:
            char_upper = char.upper()
            if char_upper != prev_char:
                compressed.append(char_upper)
            prev_char = char_upper
        
        return ''.join(compressed)
    
    def compress_with_metadata(self, word: str) -> tuple[str, dict]:
        """Compress word and return with metadata"""
        compressed = self.compress(word)
        
        metadata = {
            "original_length": len(word),
            "compressed_length": len(compressed),
            "compression_ratio": len(compressed) / len(word) if len(word) > 0 else 0,
            "vowels_removed": sum(1 for c in word if c in self.vowels),
            "doubles_removed": self._count_doubles(word)
        }
        
        return compressed, metadata
    
    def _count_doubles(self, word: str) -> int:
        """Count number of double consonants in word"""
        count = 0
        prev_char = None
        
        for char in word:
            if char not in self.vowels and char == prev_char:
                count += 1
            prev_char = char
        
        return count
    
    def decompress_hint(self, compressed: str) -> str:
        """Return decompression hint (not full word reconstruction)"""
        return ' '.join([c for c in compressed])
    
    def embed_in_emoji(self, emoji: str, compressed: str) -> str:
        """
        Embed compressed string into emoji using zero-width characters
        Each character encoded with zero-width joiner
        """
        zwj = "\u200D"
        encoded = ''.join(f"{zwj}{c}" for c in compressed)
        return f"{emoji}{encoded}"
    
    def extract_from_emoji(self, emoji_with_metadata: str) -> tuple[str, str]:
        """Extract compressed string from encoded emoji"""
        zwj = "\u200D"
        parts = emoji_with_metadata.split(zwj)
        
        emoji = parts[0]
        compressed = ''.join(parts[1:])
        
        return emoji, compressed
