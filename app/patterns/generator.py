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
        
        # Mathematical patterns
        yield from self._fibonacci_patterns()
        yield from self._prime_patterns()
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
