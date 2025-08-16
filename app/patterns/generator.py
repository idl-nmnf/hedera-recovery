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
        
        # Advanced geometric patterns
        yield from self._zigzag_patterns()
        yield from self._spiral_patterns()
        yield from self._mirror_patterns()
        yield from self._half_reverse_patterns()
        yield from self._quarter_rotation_patterns()
        yield from self._column_based_patterns()
        yield from self._chunk_reversal_patterns()
        
        # NEW: Ledger card writing patterns
        yield from self._ledger_card_patterns()
        yield from self._two_column_patterns()
        yield from self._card_writing_sequence_patterns()
        yield from self._ledger_display_order_patterns()
        yield from self._card_position_swap_patterns()
        
        # Advanced mathematical patterns
        yield from self._fibonacci_patterns()
        yield from self._prime_patterns()
        yield from self._golden_ratio_patterns()
        yield from self._modular_arithmetic_patterns()
        yield from self._palindrome_patterns()
        
        # User behavior patterns
        yield from self._keyboard_patterns()
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
    # ADVANCED GEOMETRIC PATTERNS
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
    # ADVANCED MATHEMATICAL PATTERNS  
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
    # USER BEHAVIOR PATTERNS
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
    
    # =============================================================================
    # COLUMN-BASED PATTERNS (2 columns, 4 columns, etc.)
    # =============================================================================
    
    def _column_based_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Column-based word organization patterns."""
        if self.word_count >= self.length:
            words_subset = self.words[:self.length]
            
            # === TWO COLUMN PATTERNS (12 + 12) ===
            if self.length == 24:
                col1 = words_subset[:12]  # First 12 words
                col2 = words_subset[12:]  # Last 12 words
                
                # 1. Interleave columns: 1st from col1, 1st from col2, 2nd from col1, 2nd from col2...
                interleaved = []
                for i in range(12):
                    interleaved.append(col1[i])
                    interleaved.append(col2[i])
                yield tuple(interleaved)
                
                # 2. Reverse interleave: 1st from col2, 1st from col1, 2nd from col2, 2nd from col1...
                reverse_interleaved = []
                for i in range(12):
                    reverse_interleaved.append(col2[i])
                    reverse_interleaved.append(col1[i])
                yield tuple(reverse_interleaved)
                
                # 3. Column 1 + Reversed Column 2
                yield tuple(col1 + list(reversed(col2)))
                
                # 4. Reversed Column 1 + Column 2
                yield tuple(list(reversed(col1)) + col2)
                
                # 5. Both columns reversed
                yield tuple(list(reversed(col1)) + list(reversed(col2)))
                
                # 6. Zigzag between columns (1st col1, last col2, 2nd col1, 2nd-last col2...)
                col_zigzag = []
                for i in range(12):
                    col_zigzag.append(col1[i])
                    col_zigzag.append(col2[11-i])  # Reverse index from col2
                yield tuple(col_zigzag)
                
                # 7. Reverse zigzag between columns
                rev_col_zigzag = []
                for i in range(12):
                    rev_col_zigzag.append(col2[i])
                    rev_col_zigzag.append(col1[11-i])
                yield tuple(rev_col_zigzag)
            
            # === FOUR COLUMN PATTERNS (6 + 6 + 6 + 6) ===
            if self.length >= 24:
                quarter = self.length // 4
                col1 = words_subset[:quarter]
                col2 = words_subset[quarter:quarter*2]
                col3 = words_subset[quarter*2:quarter*3]
                col4 = words_subset[quarter*3:quarter*4]
                
                # 8. Round-robin through 4 columns
                four_col_pattern = []
                for i in range(quarter):
                    four_col_pattern.extend([col1[i], col2[i], col3[i], col4[i]])
                yield tuple(four_col_pattern)
                
                # 9. Reverse round-robin
                four_col_reverse = []
                for i in range(quarter):
                    four_col_reverse.extend([col4[i], col3[i], col2[i], col1[i]])
                yield tuple(four_col_reverse)
                
                # 10. Column pairs: Col1+Col3, then Col2+Col4
                col_pairs = col1 + col3 + col2 + col4
                yield tuple(col_pairs)
                
                # 11. Diagonal pattern: Col1+Col4, then Col2+Col3
                diagonal = col1 + col4 + col2 + col3
                yield tuple(diagonal)
    
    def _chunk_reversal_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Chunk-based reversal patterns as you suggested."""
        if self.word_count >= self.length:
            words_subset = self.words[:self.length]
            
            # === 6-WORD CHUNK PATTERNS ===
            if self.length == 24:
                chunk_size = 6
                chunks = [words_subset[i:i+chunk_size] for i in range(0, self.length, chunk_size)]
                
                # 1. First 6 straight, next 6 reversed, next 6 straight, last 6 reversed
                pattern1 = []
                for i, chunk in enumerate(chunks):
                    if i % 2 == 0:  # Even chunks (0, 2) - straight
                        pattern1.extend(chunk)
                    else:  # Odd chunks (1, 3) - reversed
                        pattern1.extend(reversed(chunk))
                yield tuple(pattern1)
                
                # 2. First 6 reversed, next 6 straight, next 6 reversed, last 6 straight
                pattern2 = []
                for i, chunk in enumerate(chunks):
                    if i % 2 == 0:  # Even chunks - reversed
                        pattern2.extend(reversed(chunk))
                    else:  # Odd chunks - straight
                        pattern2.extend(chunk)
                yield tuple(pattern2)
                
                # 3. All chunks reversed except first
                pattern3 = []
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        pattern3.extend(chunk)  # First straight
                    else:
                        pattern3.extend(reversed(chunk))  # Rest reversed
                yield tuple(pattern3)
                
                # 4. All chunks reversed except last
                pattern4 = []
                for i, chunk in enumerate(chunks):
                    if i == len(chunks) - 1:
                        pattern4.extend(chunk)  # Last straight
                    else:
                        pattern4.extend(reversed(chunk))  # Rest reversed
                yield tuple(pattern4)
            
            # === 4-WORD CHUNK PATTERNS ===
            chunk_size = 4
            if self.length % chunk_size == 0:
                chunks = [words_subset[i:i+chunk_size] for i in range(0, self.length, chunk_size)]
                
                # 5. Alternating 4-word chunks (straight, reverse, straight, reverse...)
                alt_pattern = []
                for i, chunk in enumerate(chunks):
                    if i % 2 == 0:
                        alt_pattern.extend(chunk)
                    else:
                        alt_pattern.extend(reversed(chunk))
                yield tuple(alt_pattern)
            
            # === 8-WORD CHUNK PATTERNS ===
            if self.length >= 16:
                chunk_size = 8
                chunks = [words_subset[i:i+chunk_size] for i in range(0, min(self.length, 16), chunk_size)]
                
                # 6. First 8 straight, last 8 reversed
                if len(chunks) >= 2:
                    pattern = list(chunks[0]) + list(reversed(chunks[1]))
                    # Fill remaining if 24 words
                    if self.length > 16:
                        remaining = words_subset[16:]
                        pattern.extend(remaining)
                    yield tuple(pattern[:self.length])
            
            # === 3-WORD CHUNK PATTERNS ===
            chunk_size = 3
            if self.length % chunk_size == 0:
                chunks = [words_subset[i:i+chunk_size] for i in range(0, self.length, chunk_size)]
                
                # 7. Every 3rd chunk reversed
                three_pattern = []
                for i, chunk in enumerate(chunks):
                    if (i + 1) % 3 == 0:  # Every 3rd chunk
                        three_pattern.extend(reversed(chunk))
                    else:
                        three_pattern.extend(chunk)
                yield tuple(three_pattern)
    
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

    # ============================================================================
    # LEDGER CARD WRITING PATTERNS
    # ============================================================================
    
    def _ledger_card_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Patterns based on how someone writes Ledger words on a 2-column card."""
        if self.word_count >= self.length:
            # Pattern 1: Write in order, but swap first and last
            pattern = self.words[:self.length]
            if len(pattern) >= 2:
                swapped = pattern.copy()
                swapped[0], swapped[-1] = swapped[-1], swapped[0]
                yield tuple(swapped)
            
            # Pattern 2: Write odd positions first, then even positions
            odds = [word for i, word in enumerate(self.words[:self.length]) if i % 2 == 0]
            evens = [word for i, word in enumerate(self.words[:self.length]) if i % 2 == 1]
            if len(odds) + len(evens) == self.length:
                yield tuple(odds + evens)
                yield tuple(evens + odds)
    
    def _two_column_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Patterns for writing words in two columns (1-12, 13-24)."""
        if self.word_count >= self.length:
            # Column writing patterns
            half = self.length // 2
            
            # Pattern 1: Left column first (1-12), then right column (13-24)
            left_col = self.words[:half]
            right_col = self.words[half:self.length] if len(self.words) >= self.length else self.words[half:]
            if len(left_col) + len(right_col) == self.length:
                yield tuple(left_col + right_col)
                
            # Pattern 2: Right column first, then left column
            if len(left_col) + len(right_col) == self.length:
                yield tuple(right_col + left_col)
                
            # Pattern 3: Interleave columns (1, 13, 2, 14, 3, 15...)
            interleaved = []
            for i in range(half):
                if i < len(left_col):
                    interleaved.append(left_col[i])
                if i < len(right_col):
                    interleaved.append(right_col[i])
            if len(interleaved) >= self.length:
                yield tuple(interleaved[:self.length])
                
            # Pattern 4: Reverse interleave (13, 1, 14, 2, 15, 3...)
            reverse_interleaved = []
            for i in range(half):
                if i < len(right_col):
                    reverse_interleaved.append(right_col[i])
                if i < len(left_col):
                    reverse_interleaved.append(left_col[i])
            if len(reverse_interleaved) >= self.length:
                yield tuple(reverse_interleaved[:self.length])
    
    def _card_writing_sequence_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Patterns based on the sequence of writing words as they appear on Ledger."""
        if self.word_count >= self.length:
            # Pattern 1: Write words in groups of 4 (quarters)
            quarters = []
            quarter_size = self.length // 4
            for q in range(4):
                start = q * quarter_size
                end = start + quarter_size if q < 3 else self.length
                if start < len(self.words):
                    quarter = self.words[start:min(end, len(self.words))]
                    quarters.append(quarter)
            
            # Different quarter orderings
            if len(quarters) == 4:
                # Normal order: Q1, Q2, Q3, Q4
                yield tuple([word for quarter in quarters for word in quarter])
                # Reverse order: Q4, Q3, Q2, Q1
                yield tuple([word for quarter in reversed(quarters) for word in quarter])
                # Alternate: Q1, Q3, Q2, Q4
                alt_quarters = [quarters[0], quarters[2], quarters[1], quarters[3]]
                yield tuple([word for quarter in alt_quarters for word in quarter])
                # Zigzag: Q1, Q4, Q2, Q3
                zigzag_quarters = [quarters[0], quarters[3], quarters[1], quarters[2]]
                yield tuple([word for quarter in zigzag_quarters for word in quarter])
            
            # Pattern 2: Write words in groups of 6 (Ledger often shows 6 words at a time)
            if self.length == 24:
                groups = []
                for g in range(4):  # 4 groups of 6
                    start = g * 6
                    end = start + 6
                    if start < len(self.words):
                        group = self.words[start:min(end, len(self.words))]
                        groups.append(group)
                
                if len(groups) == 4:
                    # Different group orderings
                    yield tuple([word for group in groups for word in group])
                    yield tuple([word for group in reversed(groups) for word in group])
    
    def _ledger_display_order_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Patterns based on how Ledger displays words (often in chunks)."""
        if self.word_count >= self.length:
            # Pattern 1: Ledger shows words 1-8, 9-16, 17-24 in separate screens
            if self.length == 24:
                screen1 = self.words[0:8] if len(self.words) > 8 else self.words[0:len(self.words)]
                screen2 = self.words[8:16] if len(self.words) > 16 else self.words[8:len(self.words)]
                screen3 = self.words[16:24] if len(self.words) > 24 else self.words[16:len(self.words)]
                
                # Different screen orderings
                if len(screen1) + len(screen2) + len(screen3) == self.length:
                    # Normal: Screen1, Screen2, Screen3
                    yield tuple(screen1 + screen2 + screen3)
                    # Reverse: Screen3, Screen2, Screen1
                    yield tuple(screen3 + screen2 + screen1)
                    # Alternate: Screen1, Screen3, Screen2
                    yield tuple(screen1 + screen3 + screen2)
                    # Mixed: Screen2, Screen1, Screen3
                    yield tuple(screen2 + screen1 + screen3)
            
            # Pattern 2: Words written in a spiral on the card
            # Simulate writing positions 1,2,3,4 then 12,11,10,9 then 5,6,7,8 etc.
            positions = list(range(self.length))
            spiral_order = []
            
            # Create spiral writing pattern
            if self.length == 24:
                # Top row: 1,2,3,4,5,6
                spiral_order.extend([0,1,2,3,4,5])
                # Right column down: 12,18,24
                spiral_order.extend([11,17,23])
                # Bottom row left: 23,22,21,20,19
                spiral_order.extend([22,21,20,19,18])
                # Left column up: 13,7
                spiral_order.extend([12,6])
                # Inner spiral continues...
                spiral_order.extend([7,8,9,10,16,15,14,13])
                
                # Apply spiral order if we have enough words
                if len(spiral_order) >= self.length and len(self.words) >= self.length:
                    spiral_pattern = []
                    for pos in spiral_order[:self.length]:
                        if pos < len(self.words):
                            spiral_pattern.append(self.words[pos])
                    if len(spiral_pattern) == self.length:
                        yield tuple(spiral_pattern)
    
    def _card_position_swap_patterns(self) -> Generator[Tuple[str, ...], None, None]:
        """Patterns based on common position swaps when writing on card."""
        if self.word_count >= self.length:
            pattern = self.words[:self.length]
            
            # Pattern 1: Swap adjacent pairs (1↔2, 3↔4, 5↔6, etc.)
            pair_swapped = pattern.copy()
            for i in range(0, len(pair_swapped) - 1, 2):
                pair_swapped[i], pair_swapped[i + 1] = pair_swapped[i + 1], pair_swapped[i]
            yield tuple(pair_swapped)
            
            # Pattern 2: Swap positions 1↔13, 2↔14, 3↔15, etc. (column swaps)
            if self.length == 24:
                col_swapped = pattern.copy()
                for i in range(12):
                    if i + 12 < len(col_swapped):
                        col_swapped[i], col_swapped[i + 12] = col_swapped[i + 12], col_swapped[i]
                yield tuple(col_swapped)
            
            # Pattern 3: Swap first/last of each half
            half = self.length // 2
            half_swapped = pattern.copy()
            if len(half_swapped) >= 4:
                # Swap 1↔12 and 13↔24
                half_swapped[0], half_swapped[half - 1] = half_swapped[half - 1], half_swapped[0]
                half_swapped[half], half_swapped[-1] = half_swapped[-1], half_swapped[half]
                yield tuple(half_swapped)
            
            # Pattern 4: Reverse each column independently
            if self.length == 24:
                rev_cols = pattern.copy()
                # Reverse positions 1-12
                rev_cols[0:12] = reversed(rev_cols[0:12])
                # Reverse positions 13-24
                rev_cols[12:24] = reversed(rev_cols[12:24])
                yield tuple(rev_cols)
            
            # Pattern 5: Diagonal writing pattern (1,14,3,16,5,18,7,20,9,22,11,24,2,13,4,15,6,17,8,19,10,21,12,23)
            if self.length == 24:
                diagonal = []
                # First diagonal: odd positions from left column + even positions from right column
                for i in range(12):
                    if i % 2 == 0 and i < len(pattern):  # 1,3,5,7,9,11 (positions 0,2,4,6,8,10)
                        diagonal.append(pattern[i])
                    if i % 2 == 1 and i + 12 < len(pattern):  # 14,16,18,20,22,24 (positions 13,15,17,19,21,23)
                        diagonal.append(pattern[i + 12])
                
                # Second diagonal: even positions from left + odd positions from right
                for i in range(12):
                    if i % 2 == 1 and i < len(pattern):  # 2,4,6,8,10,12 (positions 1,3,5,7,9,11)
                        diagonal.append(pattern[i])
                    if i % 2 == 0 and i + 12 < len(pattern):  # 13,15,17,19,21,23 (positions 12,14,16,18,20,22)
                        diagonal.append(pattern[i + 12])
                
                if len(diagonal) == self.length:
                    yield tuple(diagonal)


def generate_combinations(words: List[str], length: int = 24) -> Generator[Tuple[str, ...], None, None]:
    """Main entry point for pattern generation."""
    generator = PatternGenerator(words, length)
    return generator.generate_all_patterns()
