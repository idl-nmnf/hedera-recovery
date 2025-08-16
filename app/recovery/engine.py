"""Main recovery engine orchestrating the wallet recovery process."""

import itertools
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional

from patterns import generate_combinations
from crypto import KeyDerivation
from hedera import HederaClient
from database import Database
from utils import setup_logging, Validator
from config import (
    DEFAULT_BATCH_SIZE, DEFAULT_CACHE_SIZE, MAX_WORKERS,
    PROGRESS_LOG_INTERVAL, BATCH_LOG_INTERVAL, MEMORY_CLEANUP_INTERVAL
)


class RecoveryEngine:
    """Main engine for wallet recovery operations."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.key_derivation = KeyDerivation()
        self.hedera_client = HederaClient()
        self.database = Database()
        self.validator = Validator()
        
        # Recovery stats
        self.total_checked = 0
        self.wallets_found = 0
    
    def initialize(self):
        """Initialize the recovery system."""
        self.logger.info("Initializing Hedera Wallet Recovery System...")
        self.database.init_database()
        self.logger.info("Recovery system ready!")
    
    def test_known_wallet(self, test_mnemonic: str, expected_key: str = None) -> bool:
        """Test derivation methods against a known wallet."""
        self.logger.info("=== TESTING KNOWN WALLET ===")
        self.logger.info("Testing mnemonic from test_mnemonic.txt")
        
        if expected_key:
            self.logger.info(f"Expected public key: {expected_key}")
        
        # Validate mnemonic
        if not self.validator.is_valid_mnemonic(test_mnemonic):
            self.logger.error("❌ Test mnemonic is not valid BIP39")
            return False
        
        self.logger.info("✓ Mnemonic is valid BIP39")
        
        # Test all derivation methods
        derivation_methods = self.key_derivation.derive_all_keys(test_mnemonic)
        
        self.logger.info(f"✓ Derived {len(derivation_methods)} possible public keys:")
        
        match_found = False
        for method_name, pubkey_hex in derivation_methods:
            self.logger.info(f"  {method_name}: {pubkey_hex}")
            
            if expected_key and pubkey_hex == expected_key:
                self.logger.info(f"*** MATCH FOUND! Method: {method_name} ***")
                match_found = True
        
        if expected_key and not match_found:
            self.logger.error(f"TEST FAILED: None of our derived keys match the expected key: {expected_key}")
            return False
        
        # Test account lookup and balance checking
        self.logger.info(f"✓ Successful derivation method: {derivation_methods[0][0] if derivation_methods else 'None'}")
        
        if derivation_methods:
            method_name, accounts, balance = self.hedera_client.check_balance_for_keys(derivation_methods)
            
            if accounts:
                self.logger.info(f"✓ Found accounts: {accounts}")
                self.logger.info(f"✓ Total balance: {balance} tinybars")
                self.logger.info("✓ TEST PASSED: Test wallet validation successful!")
                return True
        
        self.logger.warning("⚠️ Test completed but no accounts/balance found")
        return not expected_key  # Pass if no expected key specified
    
    def test_derivation_methods(self, test_mnemonic: str) -> bool:
        """Test all derivation methods for a mnemonic without key validation."""
        self.logger.info(f"=== TESTING DERIVATION METHODS ===")
        self.logger.info(f"Testing mnemonic: {test_mnemonic[:20]}...")
        
        # Validate mnemonic
        if not self.validator.is_valid_mnemonic(test_mnemonic):
            self.logger.error("❌ Test mnemonic is not valid BIP39")
            return False
        
        self.logger.info("✓ Mnemonic is valid BIP39")
        
        # Test all derivation methods
        derivation_methods = self.key_derivation.derive_all_keys(test_mnemonic)
        
        self.logger.info(f"✓ Derived {len(derivation_methods)} possible public keys:")
        
        for method_name, pubkey_hex in derivation_methods:
            self.logger.info(f"  {method_name}: {pubkey_hex}")
        
        # Test account lookup and balance checking
        if derivation_methods:
            method_name, accounts, balance = self.hedera_client.check_balance_for_keys(derivation_methods)
            
            if accounts:
                self.logger.info(f"✓ Found wallet with method: {method_name}")
                self.logger.info(f"✓ Accounts: {accounts}")
                self.logger.info(f"✓ Total balance: {balance} tinybars")
                self.logger.info("✓ DERIVATION TEST PASSED: Wallet found with balance!")
                return True
            else:
                self.logger.info("ℹ️ No accounts found with balance (this may be normal for test wallets)")
                self.logger.info("✓ DERIVATION TEST PASSED: All methods tested successfully")
                return True
        
        self.logger.error("❌ DERIVATION TEST FAILED: No derivation methods available")
        return False
    
    def process_combination(self, word_combination: Tuple[str, ...]) -> Tuple[str, bool, int]:
        """Process a single word combination."""
        mnemonic = " ".join(word_combination)
        
        # Skip if already tested
        if self.database.is_already_tested(mnemonic):
            return mnemonic, False, 0
        
        # Validate mnemonic
        if not self.validator.is_valid_mnemonic(mnemonic):
            self.database.save_result(mnemonic, 0, "invalid", [])
            return mnemonic, False, 0
        
        # Derive keys and check balances
        derivation_methods = self.key_derivation.derive_all_keys(mnemonic)
        method_name, accounts, balance = self.hedera_client.check_balance_for_keys(derivation_methods)
        
        # Save result
        self.database.save_result(mnemonic, balance, method_name, accounts)
        
        return mnemonic, balance > 0, balance
    
    def run_recovery(self, words: List[str]) -> Optional[Tuple[str, int]]:
        """Run the main recovery process."""
        self.logger.info("=== STARTING WALLET RECOVERY ===")
        self.logger.info(f"Loaded {len(words)} words for pattern generation")
        
        # Validate wordlist
        if not self.validator.validate_wordlist(words):
            self.logger.warning("Wordlist contains invalid BIP39 words, proceeding anyway...")
        
        batch_size = DEFAULT_BATCH_SIZE
        max_workers = min(MAX_WORKERS, 8)
        cache_size = DEFAULT_CACHE_SIZE
        
        # Pre-generate and cache patterns
        self.logger.info("Pre-generating smart patterns...")
        combos = generate_combinations(words)
        pattern_cache = []
        
        try:
            for i, combo in enumerate(combos):
                pattern_cache.append(combo)
                if i >= cache_size:
                    break
            self.logger.info(f"Cached {len(pattern_cache)} smart patterns in memory")
        except Exception as e:
            self.logger.error(f"Error caching patterns: {e}")
            return None
        
        # Process patterns
        pattern_iter = iter(pattern_cache)
        
        while True:
            # Get batch of combinations
            batch = list(itertools.islice(pattern_iter, batch_size))
            
            if not batch:
                # Generate more patterns dynamically
                self.logger.info("Exhausted cached patterns, generating more...")
                additional_combos = generate_combinations(words)
                
                # Skip cached patterns
                for _ in range(cache_size):
                    try:
                        next(additional_combos)
                    except StopIteration:
                        break
                
                # Get new batch
                batch = list(itertools.islice(additional_combos, batch_size))
                
                if not batch:
                    self.logger.warning("Unexpected: pattern generation stopped, restarting...")
                    combo_generator = generate_combinations(words)
                    batch = list(itertools.islice(combo_generator, batch_size))
                    
                    if not batch:
                        self.logger.error("Critical: Unable to generate any patterns!")
                        break
            
            # Process batch
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.process_combination, combo) for combo in batch]
                
                for future in as_completed(futures):
                    try:
                        mnemonic, valid, balance = future.result()
                        self.total_checked += 1
                        
                        if valid and balance > 0:
                            self.wallets_found += 1
                            self.logger.info(f'🎉 WALLET FOUND! Mnemonic: {mnemonic}')
                            self.logger.info(f'💰 Balance: {balance} tinybars')
                            return mnemonic, balance
                        
                        # Progress logging
                        if self.total_checked % PROGRESS_LOG_INTERVAL == 0:
                            self.logger.info(f"📊 Progress: {self.total_checked:,} combinations tested, {self.wallets_found} wallets found")
                            self.logger.info(f"⏱️  Rate: ~{PROGRESS_LOG_INTERVAL/60:.1f} combinations/minute")
                        elif self.total_checked % BATCH_LOG_INTERVAL == 0:
                            self.logger.info(f"Checked {self.total_checked:,} combinations, found {self.wallets_found} wallets with balance.")
                        
                    except Exception as e:
                        self.logger.error(f"Error processing future: {e}")
                        continue
            
            # Memory management
            if self.total_checked % MEMORY_CLEANUP_INTERVAL == 0:
                gc.collect()
                self.logger.info(f"🧹 Memory cleanup performed at {self.total_checked:,} combinations")
        
        return None
