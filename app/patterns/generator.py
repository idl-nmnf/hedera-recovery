"""Pattern generation strategies for mnemonic combinations."""

import itertools
import random
from typing import List, Tuple, Generator


class PatternGenerator:
    """Advanced pattern generation for wallet recovery."""
    
    def __init__(self, words: List[str], length: int = 24):
        self.words = words
        self.length = length
        self.word_count = len(words)
    
    def generate_all_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Generate all pattern types in order of likelihood."""
        # Smart patterns first (high probability)
        yield from self._exact_match_patterns()
        yield from self._sliding_window_patterns()
        yield from self._split_patterns()
        yield from self._interleaved_patterns()
        yield from self._chunk_patterns()
        
        # NEW: Advanced geometric patterns
        yield from self._zigzag_patterns()
        yield from self._spiral_patterns()
        yield from self._mirror_patterns()
        yield from self._half_reverse_patterns()
        yield from self._quarter_rotation_patterns()
        
        # NEW: Advanced mathematical patterns
        yield from self._fibonacci_patterns()
        yield from self._prime_patterns()
        yield from self._golden_ratio_patterns()
        yield from self._modular_arithmetic_patterns()
        yield from self._palindrome_patterns()
        
        # NEW: User behavior patterns
        yield from self._keyboard_patterns()
        yield from self._alphabetical_patterns()
        yield from self._frequency_patterns()
        yield from self._length_patterns()
        
        # Original mathematical patterns
        yield from self._random_seed_patterns()
        
        # Infinite patterns (will run indefinitely)
        yield from self._infinite_random_patterns()
        yield from self._systematic_combinations()
        yield from self._permutation_patterns()
        yield from self._combination_patterns()
    
    def _exact_match_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Use wordlist exactly as-is if correct length."""
        if self.word_count == self.length:
            yield tuple(self.words)
            yield tuple(reversed(self.words))
    
    def _sliding_window_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Generate overlapping sequences from wordlist."""
        if self.word_count > self.length:
            for start in range(self.word_count - self.length + 1):
                yield tuple(self.words[start:start + self.length])
                # Also try reverse of each window
                yield tuple(reversed(self.words[start:start + self.length]))
    
    def _split_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Split patterns: first N + last N words."""
        if self.word_count >= self.length:
            for split in range(1, self.length):
                first_part = self.words[:split]
                last_part = self.words[-(self.length - split):]
                if len(first_part) + len(last_part) == self.length:
                    yield tuple(first_part + last_part)
    
    def _interleaved_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Take every Nth word."""
        if self.word_count >= self.length * 2:
            for step in range(2, min(5, self.word_count // self.length + 1)):
                pattern = []
                for i in range(0, self.word_count, step):
                    pattern.append(self.words[i])
                    if len(pattern) == self.length:
                        break
                if len(pattern) == self.length:
                    yield tuple(pattern)
    
    def _chunk_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Divide wordlist into chunks, take from each."""
        if self.word_count >= self.length:
            chunk_size = self.word_count // self.length
            if chunk_size > 0:
                pattern = []
                for i in range(self.length):
                    start_idx = i * chunk_size
                    if start_idx < self.word_count:
                        pattern.append(self.words[start_idx])
                if len(pattern) == self.length:
                    yield tuple(pattern)
    
    def _fibonacci_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Select words using Fibonacci-like sequence."""
        if self.word_count >= self.length:
            fib_indices = [0, 1]
            while len(fib_indices) < self.length:
                next_idx = (fib_indices[-1] + fib_indices[-2]) % self.word_count
                fib_indices.append(next_idx)
            
            yield tuple(self.words[i] for i in fib_indices[:self.length])
    
    def _prime_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Select words at prime positions."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        if self.word_count >= self.length:
            prime_pattern = []
            for i in range(self.length):
                if i < len(primes) and primes[i] < self.word_count:
                    prime_pattern.append(self.words[primes[i]])
                else:
                    prime_pattern.append(self.words[i % self.word_count])
            yield tuple(prime_pattern)

    # =============================================================================
    # NEW ADVANCED GEOMETRIC PATTERNS
    # =============================================================================
    
    def _zigzag_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Zigzag patterns: start->end->second->second_last, etc."""
        if self.word_count >= self.length:
            # Classic zigzag
            pattern = []
            left, right = 0, self.word_count - 1
            for i in range(self.length):
                if i % 2 == 0:
                    pattern.append(self.words[left])
                    left += 1
                else:
                    pattern.append(self.words[right])
                    right -= 1
                if left > right:
                    break
            if len(pattern) == self.length:
                yield tuple(pattern)
            
            # Reverse zigzag (start from end)
            pattern = []
            left, right = 0, self.word_count - 1
            for i in range(self.length):
                if i % 2 == 0:
                    pattern.append(self.words[right])
                    right -= 1
                else:
                    pattern.append(self.words[left])
                    left += 1
                if left > right:
                    break
            if len(pattern) == self.length:
                yield tuple(pattern)
    
    def _spiral_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Spiral inward and outward from center."""
        if self.word_count >= self.length:
            center = self.word_count // 2
            
            # Spiral outward from center
            pattern = []
            visited = set()
            pattern.append(self.words[center])
            visited.add(center)
            
            offset = 1
            while len(pattern) < self.length and offset <= center:
                # Add left and right of center
                for pos in [center - offset, center + offset]:
                    if 0 <= pos < self.word_count and pos not in visited and len(pattern) < self.length:
                        pattern.append(self.words[pos])
                        visited.add(pos)
                offset += 1
            
            if len(pattern) == self.length:
                yield tuple(pattern)
    
    def _mirror_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Mirror patterns: first half normal, second half reversed."""
        if self.word_count >= self.length:
            half = self.length // 2
            
            # First half + reversed second half
            if self.word_count >= half * 2:
                first_half = self.words[:half]
                second_half = list(reversed(self.words[half:half * 2]))
                yield tuple(first_half + second_half)
            
            # All words reversed in place
            yield tuple(reversed(self.words[:self.length]))
    
    def _half_reverse_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Various half-reverse patterns as you suggested."""
        if self.word_count >= self.length:
            half = self.length // 2
            
            # First half straight, second half reverse
            if self.word_count >= self.length:
                first_half = self.words[:half]
                remaining_words = self.words[half:self.length]
                second_half = list(reversed(remaining_words))
                yield tuple(first_half + second_half)
            
            # First half reverse, second half straight  
            if self.word_count >= self.length:
                first_half = list(reversed(self.words[:half]))
                second_half = self.words[half:self.length]
                yield tuple(first_half + second_half)
            
            # Alternating reverse chunks (every 4 words)
            pattern = []
            chunk_size = 4
            for i in range(0, self.length, chunk_size):
                chunk = self.words[i:min(i + chunk_size, self.length)]
                if (i // chunk_size) % 2 == 1:  # Reverse every second chunk
                    chunk = list(reversed(chunk))
                pattern.extend(chunk)
            if len(pattern) >= self.length:
                yield tuple(pattern[:self.length])
    
    def _quarter_rotation_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Rotate by quarters, thirds, etc."""
        if self.word_count >= self.length:
            words_subset = self.words[:self.length]
            
            # Rotate by quarters
            for quarter in [6, 12, 18]:  # 24/4, 24/2, 24*3/4
                if quarter < self.length:
                    rotated = words_subset[quarter:] + words_subset[:quarter]
                    yield tuple(rotated)
            
            # Rotate by thirds  
            for third in [8, 16]:  # 24/3, 24*2/3
                if third < self.length:
                    rotated = words_subset[third:] + words_subset[:third]
                    yield tuple(rotated)

    # =============================================================================
    # NEW ADVANCED MATHEMATICAL PATTERNS  
    # =============================================================================
    
    def _golden_ratio_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Use golden ratio for word selection."""
        if self.word_count >= self.length:
            phi = 1.618033988749
            pattern = []
            for i in range(self.length):
                index = int((i * phi) % self.word_count)
                pattern.append(self.words[index])
            yield tuple(pattern)
    
    def _modular_arithmetic_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Patterns based on modular arithmetic."""
        if self.word_count >= self.length:
            for mod in [3, 5, 7, 11]:  # Different modular bases
                pattern = []
                for i in range(self.length):
                    index = (i * mod + i) % self.word_count
                    pattern.append(self.words[index])
                yield tuple(pattern)
    
    def _palindrome_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Create palindromic word patterns."""
        if self.word_count >= self.length // 2:
            half_length = self.length // 2
            first_half = self.words[:half_length]
            
            # Perfect palindrome
            if self.length % 2 == 0:
                palindrome = first_half + list(reversed(first_half))
            else:
                # Odd length - add middle word
                middle = [self.words[half_length]] if half_length < self.word_count else [self.words[0]]
                palindrome = first_half + middle + list(reversed(first_half))
            
            if len(palindrome) == self.length:
                yield tuple(palindrome)

    # =============================================================================
    # NEW USER BEHAVIOR PATTERNS
    # =============================================================================
    
    def _keyboard_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Patterns based on keyboard layouts (QWERTY-like selection)."""
        if self.word_count >= self.length:
            # QWERTY row pattern simulation
            qwerty_indices = [0, 9, 4, 17, 19, 24, 20, 8, 15, 16, 1, 18, 3, 6, 7, 10, 11, 25, 23, 2, 13, 21, 22, 14]
            pattern = []
            for i in range(self.length):
                if i < len(qwerty_indices):
                    index = qwerty_indices[i] % self.word_count
                else:
                    index = i % self.word_count
                pattern.append(self.words[index])
            yield tuple(pattern)
    
    def _alphabetical_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Comprehensive alphabetical sorting patterns."""
        if self.word_count >= self.length:
            # === BASIC ALPHABETICAL PATTERNS ===
            sorted_words = sorted(self.words)
            
            # 1. First N alphabetically (A-Z order)
            yield tuple(sorted_words[:self.length])
            
            # 2. Last N alphabetically (Z-A end of alphabet)
            yield tuple(sorted_words[-self.length:])
            
            # 3. REVERSE alphabetical order (Z-A)
            reverse_sorted = sorted(self.words, reverse=True)
            yield tuple(reverse_sorted[:self.length])
            
            # 4. Every nth alphabetically (distributed sampling)
            if len(sorted_words) > self.length:
                step = len(sorted_words) // self.length
                pattern = [sorted_words[i * step] for i in range(self.length)]
                yield tuple(pattern)
            
            # === ADVANCED ALPHABETICAL PATTERNS ===
            
            # 5. Alphabetical zigzag (A, Z, B, Y, C, X, ...)
            left_idx, right_idx = 0, len(sorted_words) - 1
            alpha_zigzag = []
            for i in range(min(self.length, len(sorted_words))):
                if i % 2 == 0:
                    alpha_zigzag.append(sorted_words[left_idx])
                    left_idx += 1
                else:
                    alpha_zigzag.append(sorted_words[right_idx])
                    right_idx -= 1
                if left_idx > right_idx:
                    break
            if len(alpha_zigzag) == self.length:
                yield tuple(alpha_zigzag)
            
            # 6. Middle-out alphabetical (start from middle of alphabet)
            if len(sorted_words) >= self.length:
                mid = len(sorted_words) // 2
                middle_out = []
                for i in range(self.length // 2):
                    if mid + i < len(sorted_words):
                        middle_out.append(sorted_words[mid + i])
                    if mid - i - 1 >= 0 and len(middle_out) < self.length:
                        middle_out.append(sorted_words[mid - i - 1])
                if len(middle_out) >= self.length:
                    yield tuple(middle_out[:self.length])
            
            # === ALPHABETICAL BY WORD CHARACTERISTICS ===
            
            # 7. Sort by first letter, then by length
            by_first_then_length = sorted(self.words, key=lambda x: (x[0], len(x)))
            yield tuple(by_first_then_length[:self.length])
            
            # 8. Sort by last letter
            by_last_letter = sorted(self.words, key=lambda x: x[-1])
            yield tuple(by_last_letter[:self.length])
            
            # 9. Reverse sort by last letter
            by_last_letter_rev = sorted(self.words, key=lambda x: x[-1], reverse=True)
            yield tuple(by_last_letter_rev[:self.length])
            
            # 10. Sort by middle letter (for words long enough)
            def get_middle_char(word):
                return word[len(word) // 2] if len(word) > 0 else 'z'
            
            by_middle_letter = sorted(self.words, key=get_middle_char)
            yield tuple(by_middle_letter[:self.length])
            
            # === VOWEL/CONSONANT ALPHABETICAL PATTERNS ===
            
            # 11. Vowels first alphabetically, then consonants
            vowels = [w for w in sorted_words if w[0].lower() in 'aeiou']
            consonants = [w for w in sorted_words if w[0].lower() not in 'aeiou']
            vowel_consonant_pattern = (vowels + consonants)[:self.length]
            if len(vowel_consonant_pattern) == self.length:
                yield tuple(vowel_consonant_pattern)
            
            # 12. Consonants first, then vowels
            consonant_vowel_pattern = (consonants + vowels)[:self.length]
            if len(consonant_vowel_pattern) == self.length:
                yield tuple(consonant_vowel_pattern)
            
            # === ALTERNATING ALPHABETICAL PATTERNS ===
            
            # 13. Alternating A-Z and Z-A
            alternating_alpha = []
            for i in range(self.length):
                if i % 2 == 0 and i < len(sorted_words):
                    alternating_alpha.append(sorted_words[i])
                elif len(reverse_sorted) > i // 2:
                    alternating_alpha.append(reverse_sorted[i // 2])
            if len(alternating_alpha) == self.length:
                yield tuple(alternating_alpha)
            
            # 14. Alphabetical by word position (1st, 3rd, 5th... then 2nd, 4th, 6th...)
            if len(sorted_words) >= self.length:
                odd_positions = [sorted_words[i] for i in range(0, len(sorted_words), 2)]
                even_positions = [sorted_words[i] for i in range(1, len(sorted_words), 2)]
                position_pattern = (odd_positions + even_positions)[:self.length]
                yield tuple(position_pattern)
    
    def _frequency_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Patterns based on word length or characteristics."""
        if self.word_count >= self.length:
            # Sort by word length
            by_length = sorted(self.words, key=len)
            yield tuple(by_length[:self.length])
            yield tuple(by_length[-self.length:])
            
            # Sort by first letter
            by_first_letter = sorted(self.words, key=lambda x: x[0])
            yield tuple(by_first_letter[:self.length])
    
    def _length_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Patterns based on word lengths."""
        if self.word_count >= self.length:
            # Shortest words first
            shortest = sorted(self.words, key=len)[:self.length]
            yield tuple(shortest)
            
            # Longest words first
            longest = sorted(self.words, key=len, reverse=True)[:self.length]
            yield tuple(longest)
            
            # Alternating short/long
            short_words = sorted([w for w in self.words if len(w) <= 5], key=len)
            long_words = sorted([w for w in self.words if len(w) > 5], key=len, reverse=True)
            
            pattern = []
            for i in range(self.length):
                if i % 2 == 0 and short_words:
                    pattern.append(short_words.pop(0))
                elif long_words:
                    pattern.append(long_words.pop(0))
                elif short_words:
                    pattern.append(short_words.pop(0))
                else:
                    pattern.append(self.words[i % self.word_count])
            
            if len(pattern) == self.length:
                yield tuple(pattern)
    
    def _random_seed_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Multiple random seeds for diversity."""
        word_indices = list(range(self.word_count))
        
        for seed in [42, 123, 456, 789, 999, 1337, 2024, 8888, 12345]:
            random.seed(seed)
            for _ in range(min(5000, self.word_count * 10)):
                if self.word_count >= self.length:
                    sampled_indices = random.sample(word_indices, self.length)
                    pattern = tuple(self.words[i] for i in sampled_indices)
                    yield pattern
    
    def _infinite_random_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Infinite random pattern generation."""
        random.seed(42)  # Reset to deterministic seed
        word_indices = list(range(self.word_count))
        
        if self.word_count >= self.length:
            while True:
                sampled_indices = random.sample(word_indices, self.length)
                pattern = tuple(self.words[i] for i in sampled_indices)
                yield pattern
    
    def _systematic_combinations(self) -> Generator[Tuple[str, ...], None, None]:
        """All possible combinations with repetition (infinite)."""
        for combo in itertools.product(self.words, repeat=self.length):
            yield combo
    
    def _permutation_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """All possible orderings of words from wordlist."""
        if self.word_count >= self.length:
            for combo in itertools.permutations(self.words, self.length):
                yield combo
    
    def _combination_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """All possible combinations without repetition."""
        if self.word_count >= self.length:
            for combo in itertools.combinations(self.words, self.length):
                yield combo


def generate_combinations(words: List[str], length: int = 24) -> Generator[Tuple[str, ...], None, None]:
    """Main entry point for pattern generation."""
    generator = PatternGenerator(words, length)
    return generator.generate_all_patterns()
