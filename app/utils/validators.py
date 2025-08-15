"""Input validation utilities."""

from mnemonic import Mnemonic
from typing import List


class Validator:
    """Input validation for recovery operations."""
    
    def __init__(self):
        self.mnemo = Mnemonic('english')
    
    def is_valid_mnemonic(self, mnemonic: str) -> bool:
        """Check if mnemonic is valid BIP39."""
        return self.mnemo.check(mnemonic)
    
    def validate_wordlist(self, words: List[str]) -> bool:
        """Validate that wordlist contains valid BIP39 words."""
        valid_words = set(self.mnemo.wordlist)
        invalid_words = [word for word in words if word not in valid_words]
        
        if invalid_words:
            print(f"Warning: Invalid BIP39 words found: {invalid_words}")
            return False
        
        return True
    
    def sanitize_mnemonic(self, mnemonic: str) -> str:
        """Clean and normalize mnemonic input."""
        # Remove extra whitespace and normalize
        words = mnemonic.strip().lower().split()
        return " ".join(words)
