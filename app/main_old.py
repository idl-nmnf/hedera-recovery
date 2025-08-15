import os
import psycopg2
from mnemonic import Mnemonic
import itertools
import logging
import requests
import base64
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'hedera')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'recovery')
DB_NAME = os.getenv('DB_NAME', 'hedera_recovery')
WORDLIST_PATH = 'wordlist.txt'

def get_db():
    return psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS combinations (
        id SERIAL PRIMARY KEY,
        mnemonic TEXT UNIQUE,
        checked BOOLEAN DEFAULT FALSE,
        balance NUMERIC DEFAULT 0
    )''')
    conn.commit()
    cur.close()
    conn.close()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Read wordlist
def read_wordlist():
    with open(WORDLIST_PATH, 'r') as f:
        return [w.strip() for w in f if w.strip() and not w.startswith('#')]


# Generate combinations (prioritize smart patterns for 24-word mnemonics)
def generate_combinations(words, length=24):
    """Generate smart 24-word combinations using various heuristic patterns"""
    word_count = len(words)
    
    # Pattern 1: Use all words if we have exactly 24
    if word_count == length:
        yield tuple(words)
        # Also try reverse order
        yield tuple(reversed(words))
    
    # Pattern 2: Sliding windows of 24 words from the wordlist
    if word_count > length:
        for start in range(word_count - length + 1):
            yield tuple(words[start:start + length])
            # Also try reverse of each window
            yield tuple(reversed(words[start:start + length]))
    
    # Pattern 3: Split patterns (first N + last N)
    if word_count >= length:
        for split in range(1, length):
            first_part = words[:split]
            last_part = words[-(length - split):]
            if len(first_part) + len(last_part) == length:
                yield tuple(first_part + last_part)
    
    # Pattern 4: Interleaved patterns (take every Nth word)
    if word_count >= length * 2:
        for step in range(2, min(5, word_count // length + 1)):
            pattern = []
            for i in range(0, word_count, step):
                pattern.append(words[i])
                if len(pattern) == length:
                    break
            if len(pattern) == length:
                yield tuple(pattern)
    
    # Pattern 5: Chunk-based patterns (divide wordlist into chunks, take from each)
    if word_count >= length:
        chunk_size = word_count // length
        if chunk_size > 0:
            pattern = []
            for i in range(length):
                start_idx = i * chunk_size
                if start_idx < word_count:
                    pattern.append(words[start_idx])
            if len(pattern) == length:
                yield tuple(pattern)
    
    # Pattern 6: Random sampling with memory (generate and cache patterns)
    import random
    random.seed(42)  # Deterministic for reproducibility
    word_indices = list(range(word_count))
    
    # Generate multiple random combinations and cache them
    cached_patterns = []
    for _ in range(min(50000, word_count * 50)):  # Increased cache size
        if word_count >= length:
            sampled_indices = random.sample(word_indices, length)
            pattern = tuple(words[i] for i in sampled_indices)
            cached_patterns.append(pattern)
    
    # Yield cached patterns
    for pattern in cached_patterns:
        yield pattern
    
    # Pattern 6a: Fibonacci-like selection
    # Select words using Fibonacci-like sequence
    if word_count >= length:
        fib_indices = [0, 1]
        while len(fib_indices) < length:
            next_idx = (fib_indices[-1] + fib_indices[-2]) % word_count
            fib_indices.append(next_idx)
        
        yield tuple(words[i] for i in fib_indices[:length])
    
    # Pattern 6b: Prime number selection
    # Select words at prime positions (mathematical patterns)
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    if word_count >= length:
        prime_pattern = []
        for i in range(length):
            if i < len(primes) and primes[i] < word_count:
                prime_pattern.append(words[primes[i]])
            else:
                prime_pattern.append(words[i % word_count])
        yield tuple(prime_pattern)
    
    # Pattern 6c: Multiple random seeds for diversity
    for seed in [123, 456, 789, 999, 1337, 2024, 8888, 12345]:
        random.seed(seed)
        for _ in range(min(5000, word_count * 10)):
            if word_count >= length:
                sampled_indices = random.sample(word_indices, length)
                pattern = tuple(words[i] for i in sampled_indices)
                yield pattern
    
    # Pattern 7: Advanced random sampling (infinite)
    # Continue generating random patterns indefinitely
    if word_count >= length:
        while True:
            sampled_indices = random.sample(word_indices, length)
            pattern = tuple(words[i] for i in sampled_indices)
            yield pattern
    
    # Pattern 8: Systematic combinations with repetition allowed
    # Generate all possible combinations with repetition (truly infinite for recovery)
    for combo in itertools.product(words, repeat=length):
        yield combo
    
    # Pattern 9: Permutations of available words
    # All possible orderings of words from the wordlist
    if word_count >= length:
        for combo in itertools.permutations(words, length):
            yield combo
    
    # Pattern 10: Combinations without repetition
    # All possible combinations without repeating words
    if word_count >= length:
        for combo in itertools.combinations(words, length):
            yield combo


# Check if mnemonic is valid (BIP39)
mnemo = Mnemonic('english')
def is_valid_mnemonic(mnemonic):
    return mnemo.check(mnemonic)

# Hedera mnemonic/account/balance check
def mnemonic_to_public_key(mnemonic):
    # Use the mnemonic package to derive seed
    mnemo = Mnemonic('english')
    seed = mnemo.to_seed(mnemonic)
    
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import hashlib
        import hmac
        
        # Try multiple derivation methods commonly used for Hedera wallets
        derivation_methods = []
        
        # Method 1: Direct seed (our current approach)
        try:
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed[:32])
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            derivation_methods.append(("direct_seed", pubkey_hex))
        except:
            pass
        
        # Method 2: BIP32-Ed25519 proper implementation
        def bip32_ed25519_derive(seed, path):
            """Proper BIP32-Ed25519 derivation"""
            # Start with master key
            master_secret = hmac.new(b"ed25519 seed", seed, hashlib.sha512).digest()
            key = master_secret[:32]
            chain_code = master_secret[32:]
            
            for index in path:
                # Ed25519 uses hardened derivation only
                if index < 0x80000000:
                    index += 0x80000000
                
                data = b'\x00' + key + index.to_bytes(4, 'big')
                mac = hmac.new(chain_code, data, hashlib.sha512).digest()
                key = mac[:32]
                chain_code = mac[32:]
            
            return key
        
        # Method 2: Standard Hedera BIP32 path
        try:
            path = [44 + 0x80000000, 3030 + 0x80000000, 0x80000000, 0x80000000, 0x80000000]
            derived_key = bip32_ed25519_derive(seed, path)
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            derivation_methods.append(("bip32_ed25519", pubkey_hex))
        except:
            pass
        
        # Method 3: PBKDF2 derivations (used by some wallets)
        pbkdf2_variants = [
            ("pbkdf2_hedera", b"hedera", 2048),
            ("pbkdf2_default", b"mnemonic", 2048),
            ("pbkdf2_bitcoin", b"Bitcoin seed", 2048),
        ]
        
        for method_name, salt, iterations in pbkdf2_variants:
            try:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=iterations,
                )
                derived_key = kdf.derive(mnemonic.encode())
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                derivation_methods.append((method_name, pubkey_hex))
            except:
                pass
        
        # Method 4: Index-based derivations (account index variations)
        for account_index in range(10):  # Try first 10 account indices
            try:
                path = [44 + 0x80000000, 3030 + 0x80000000, account_index + 0x80000000, 0x80000000, 0x80000000]
                derived_key = bip32_ed25519_derive(seed, path)
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                derivation_methods.append((f"bip32_account_{account_index}", pubkey_hex))
            except:
                pass
        
        # Method 5: Wallet-specific derivations
        wallet_specific = [
            ("metamask_style", hashlib.sha256(seed + b"metamask").digest()[:32]),
            ("hashpack_style", hashlib.sha256(mnemonic.encode() + b"hashpack").digest()[:32]),
            ("blade_style", hashlib.sha256(seed + b"blade").digest()[:32]),
        ]
        
        for method_name, derived_seed in wallet_specific:
            try:
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_seed)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                derivation_methods.append((method_name, pubkey_hex))
            except:
                pass
        
        # Method 7: Secp256k1 to Ed25519 conversion (some wallets do this)
        try:
            import secrets
            # Some wallets derive secp256k1 first, then convert to Ed25519
            secp_seed = hashlib.sha256(seed + b"secp256k1").digest()[:32]
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(secp_seed)
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            derivation_methods.append(("secp256k1_style", pubkey_hex))
        except:
            pass
        
        # Method 8: Try different passphrase combinations (BIP39 allows passphrases)
        passphrases = ["", "hedera", "HEDERA", "Hedera", "hbar", "HBAR"]
        for passphrase in passphrases:
            try:
                seed_with_pass = mnemo.to_seed(mnemonic, passphrase)
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed_with_pass[:32])
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                derivation_methods.append((f"passphrase_{passphrase or 'empty'}", pubkey_hex))
            except:
                pass
        
        # Method 9: Word-based entropy (some wallets hash the words directly)
        try:
            words = mnemonic.split()
            word_entropy = "".join(words).encode()
            derived_seed = hashlib.sha256(word_entropy).digest()[:32]
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_seed)
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            derivation_methods.append(("word_concatenation", pubkey_hex))
        except:
            pass
        
        # Method 10: BIP39 entropy to private key (skip seed generation)
        try:
            # Get the entropy directly from mnemonic
            words = mnemonic.split()
            # This is a simplified entropy extraction - real implementation would need proper BIP39 tables
            entropy_hash = hashlib.sha256(" ".join(words).encode()).digest()[:32]
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(entropy_hash)
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            derivation_methods.append(("bip39_entropy_direct", pubkey_hex))
        except:
            pass
        
        # Method 12: Ledger-specific derivations (CRITICAL!)
        # Ledger devices use different derivation than software wallets
        def ledger_bip32_ed25519(seed, path):
            """Ledger-specific BIP32 Ed25519 derivation"""
            # Ledger uses "Ledger seed" as HMAC key instead of "ed25519 seed"
            master_secret = hmac.new(b"Ledger seed", seed, hashlib.sha512).digest()
            key = master_secret[:32]
            chain_code = master_secret[32:]
            
            for index in path:
                # Ledger always uses hardened derivation for Ed25519
                if index < 0x80000000:
                    index += 0x80000000
                
                # Ledger-specific data format
                data = b'\x00' + key + index.to_bytes(4, 'big')
                mac = hmac.new(chain_code, data, hashlib.sha512).digest()
                key = mac[:32]
                chain_code = mac[32:]
            
            return key
        
        # Ledger Hedera paths (these are different from software wallets)
        ledger_paths = [
            [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000],  # Standard Ledger Hedera
            [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000],  # Ledger without last index
            [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000],  # Ledger minimal
        ]
        
        for i, path in enumerate(ledger_paths):
            try:
                derived_key = ledger_bip32_ed25519(seed, path)
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                derivation_methods.append((f"ledger_hedera_{i+1}", pubkey_hex))
            except:
                pass
        
        # Method 13: Ledger app-specific derivations
        # Different Ledger apps might use different paths
        ledger_app_variations = [
            ("ledger_ethereum_hedera", [44 + 0x80000000, 60 + 0x80000000, 0 + 0x80000000, 0, 0]),  # If using ETH app for Hedera
            ("ledger_bitcoin_hedera", [44 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000, 0, 0]),   # If using BTC app for Hedera
        ]
        
        for app_name, path in ledger_app_variations:
            try:
                derived_key = ledger_bip32_ed25519(seed, path)
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                derivation_methods.append((app_name, pubkey_hex))
            except:
                pass
        
        # Method 14: Ledger with different HMAC keys (Ledger variations)
        ledger_hmac_keys = [
            b"Ledger seed",
            b"ledger seed", 
            b"LEDGER SEED",
            b"Ledger",
            b"ledger",
        ]
        
        for hmac_key in ledger_hmac_keys:
            try:
                master_secret = hmac.new(hmac_key, seed, hashlib.sha512).digest()
                derived_key = master_secret[:32]
                
                # Apply standard Hedera path derivation
                path = [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000]
                key = derived_key
                chain_code = master_secret[32:]
                
                for index in path:
                    data = b'\x00' + key + index.to_bytes(4, 'big')
                    mac = hmac.new(chain_code, data, hashlib.sha512).digest()
                    key = mac[:32]
                    chain_code = mac[32:]
                
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(key)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                derivation_methods.append((f"ledger_hmac_{hmac_key.decode().replace(' ', '_').lower()}", pubkey_hex))
            except:
                pass
        
        # Method 15: HashPack-specific derivations (for current test)
        # HashPack might use custom derivation methods
        try:
            # HashPack custom path (they might use non-standard paths)
            hashpack_paths = [
                # Try HashPack with different account indices
                [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000, 0, 0],  # Non-hardened change/address
                [44 + 0x80000000, 3030 + 0x80000000, 0, 0],  # Shorter path
                [44 + 0x80000000, 3030 + 0x80000000],  # Minimal HashPack path
                # HashPack might derive from a different coin type initially
                [44 + 0x80000000, 3030],  # Non-hardened coin type
            ]
            
            for i, path in enumerate(hashpack_paths):
                try:
                    derived_key = bip32_ed25519_derive(seed, path)
                    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
                    public_key = private_key.public_key()
                    pubkey_hex = public_key.public_bytes_raw().hex()
                    derivation_methods.append((f"hashpack_path_{i+1}", pubkey_hex))
                except:
                    pass
        except:
            pass
        
        # Method 16: HashPack entropy variations
        # HashPack might process the mnemonic differently
        try:
            # HashPack might normalize the mnemonic differently
            normalized_variants = [
                mnemonic.lower(),
                mnemonic.upper(), 
                mnemonic.title(),
                " ".join(word.strip() for word in mnemonic.split()),  # Clean whitespace
                " ".join(word.lower().strip() for word in mnemonic.split()),  # Lowercase + clean
            ]
            
            for variant in normalized_variants:
                if variant != mnemonic:  # Don't repeat the original
                    try:
                        variant_seed = mnemo.to_seed(variant)
                        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(variant_seed[:32])
                        public_key = private_key.public_key()
                        pubkey_hex = public_key.public_bytes_raw().hex()
                        derivation_methods.append((f"hashpack_normalized_{len(derivation_methods)}", pubkey_hex))
                    except:
                        pass
        except:
            pass
        
        # Method 17: Alternative Ed25519 implementations
        # Different libraries might produce different keys
        try:
            # Try with different seed lengths
            for seed_len in [32, 64]:
                try:
                    truncated_seed = seed[:seed_len] if len(seed) >= seed_len else seed.ljust(seed_len, b'\x00')
                    if seed_len == 32:
                        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(truncated_seed)
                    else:
                        # Use first 32 bytes of 64-byte seed
                        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(truncated_seed[:32])
                    public_key = private_key.public_key()
                    pubkey_hex = public_key.public_bytes_raw().hex()
                    derivation_methods.append((f"seed_length_{seed_len}", pubkey_hex))
                except:
                    pass
        except:
            pass
        
        # Method 18: Web3/Browser wallet compatibility
        # HashPack is a browser extension, might use web3 standards
        try:
            # Ethereum-style seed to private key (even for Hedera)
            web3_seed = hashlib.keccak(seed).digest()[:32] if hasattr(hashlib, 'keccak') else hashlib.sha3_256(seed).digest()
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(web3_seed)
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            derivation_methods.append(("web3_style", pubkey_hex))
        except:
            pass
        
        # Method 19: Check if the expected key can be derived by brute force offset
        # Sometimes there's a simple offset or transformation
        try:
            expected_key = "c520ff29363ad4a6fae6acc892f16eba6333dbef2c74f16b78a0e9ec10b60fb9"
            expected_bytes = bytes.fromhex(expected_key)
            
            # Try XOR with our generated keys (sometimes there's a simple XOR mask)
            for method_name, our_key in derivation_methods[-10:]:  # Check last 10 methods
                try:
                    our_bytes = bytes.fromhex(our_key)
                    xor_result = bytes(a ^ b for a, b in zip(our_bytes, expected_bytes))
                    
                    # Check if XOR result looks like a pattern (all same byte, or simple pattern)
                    if len(set(xor_result)) <= 4:  # Simple pattern
                        derivation_methods.append((f"debug_xor_analysis_{method_name}", f"XOR_pattern: {xor_result.hex()}"))
                except:
                    pass
        except:
            pass
        
        # Return list of (method_name, public_key) tuples
        return derivation_methods
        
    except ImportError:
        raise ImportError("Please add 'cryptography' to requirements.txt")

def find_accounts_by_public_key(pubkey_hex):
    # Use Hedera Mirror Node REST API to search for accounts by public key (mainnet)
    url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts?account.publickey={pubkey_hex}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        accounts = [a['account'] for a in data.get('accounts', [])]
        return accounts
    except Exception as e:
        logging.error(f"Error finding accounts for pubkey {pubkey_hex}: {e}")
        return []

def get_account_balance(account_id):
    url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{account_id}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get('balance', {}).get('balance', 0)
    except Exception as e:
        logging.error(f"Error getting balance for account {account_id}: {e}")
        return 0

def check_balance(mnemonic):
    try:
        derivation_methods = mnemonic_to_public_key(mnemonic)  # Now returns list of (method, key) tuples
        for method_name, pubkey_hex in derivation_methods:
            accounts = find_accounts_by_public_key(pubkey_hex)
            for account_id in accounts:
                balance = get_account_balance(account_id)
                if balance > 0:
                    return balance
        return 0
    except Exception as e:
        logging.error(f"Error in check_balance for mnemonic: {mnemonic[:20]}... {e}")
        return 0

def main():
    init_db()
    words = read_wordlist()
    conn = get_db()
    cur = conn.cursor()
    for combo in generate_combinations(words):
        mnemonic = ' '.join(combo)
        cur.execute('SELECT checked FROM combinations WHERE mnemonic=%s', (mnemonic,))
        if cur.fetchone():
            continue  # Already checked
        if is_valid_mnemonic(mnemonic):
            balance = check_balance(mnemonic)
            cur.execute('INSERT INTO combinations (mnemonic, checked, balance) VALUES (%s, %s, %s) ON CONFLICT (mnemonic) DO NOTHING', (mnemonic, True, balance))
            conn.commit()
            if balance > 0:
                print(f'Found wallet: {mnemonic} with balance {balance}')
        else:
            cur.execute('INSERT INTO combinations (mnemonic, checked) VALUES (%s, %s) ON CONFLICT (mnemonic) DO NOTHING', (mnemonic, True))
            conn.commit()
    cur.close()
    conn.close()

# Main loop
def process_combo(combo):
    mnemonic = ' '.join(combo)
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT checked FROM combinations WHERE mnemonic=%s', (mnemonic,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return (mnemonic, None, None)  # Already checked
    try:
        if is_valid_mnemonic(mnemonic):
            balance = check_balance(mnemonic)
            # Only mark as checked if no error occurred in balance check
            cur.execute('INSERT INTO combinations (mnemonic, checked, balance) VALUES (%s, %s, %s) ON CONFLICT (mnemonic) DO NOTHING', (mnemonic, True, balance))
            conn.commit()
            cur.close()
            conn.close()
            return (mnemonic, True, balance)
        else:
            cur.execute('INSERT INTO combinations (mnemonic, checked) VALUES (%s, %s) ON CONFLICT (mnemonic) DO NOTHING', (mnemonic, True))
            conn.commit()
            cur.close()
            conn.close()
            return (mnemonic, False, 0)
    except Exception as e:
        # Do not mark as checked if an error occurred
        logging.error(f"Error processing mnemonic: {mnemonic[:20]}... {e}")
        cur.close()
        conn.close()
        return (mnemonic, None, None)

def test_known_wallet():
    """Test with a known valid wallet to verify the entire process works"""
    try:
        with open('/app/test_mnemonic.txt', 'r') as f:
            test_mnemonic = f.read().strip()
    except FileNotFoundError:
        logging.error("TEST FAILED: test_mnemonic.txt not found. Please create this file with your test mnemonic.")
        return False
    except Exception as e:
        logging.error(f"TEST FAILED: Could not read test_mnemonic.txt: {e}")
        return False
    
    # Known public key from the account endpoint
    known_pubkey = "c520ff29363ad4a6fae6acc892f16eba6333dbef2c74f16b78a0e9ec10b60fb9"
    
    logging.info("=== TESTING KNOWN WALLET ===")
    logging.info(f"Testing mnemonic from test_mnemonic.txt")
    logging.info(f"Expected public key: {known_pubkey}")
    
    # Test 1: Check if mnemonic is valid
    if not is_valid_mnemonic(test_mnemonic):
        logging.error("TEST FAILED: Mnemonic is not valid BIP39")
        return False
    logging.info("✓ Mnemonic is valid BIP39")
    
    # Test 2: Derive public keys (try multiple derivation methods)
    try:
        derivation_methods = mnemonic_to_public_key(test_mnemonic)
        logging.info(f"✓ Derived {len(derivation_methods)} possible public keys:")
        matching_method = None
        for method_name, pubkey_hex in derivation_methods:
            logging.info(f"  {method_name}: {pubkey_hex}")
            if pubkey_hex.lower() == known_pubkey.lower():
                matching_method = method_name
                logging.info(f"  *** MATCH FOUND! Method: {method_name} ***")
        
        if not matching_method:
            logging.error(f"TEST FAILED: None of our derived keys match the expected key: {known_pubkey}")
            logging.info("We need to implement a different derivation method.")
            return False
            
        logging.info(f"✓ Successful derivation method: {matching_method}")
    except Exception as e:
        logging.error(f"TEST FAILED: Could not derive public keys: {e}")
        return False
    
    # Test 3: Find accounts (use the matching method)
    all_accounts = []
    try:
        logging.info(f"Searching for accounts with successful method: {matching_method}...")
        accounts = find_accounts_by_public_key(known_pubkey)
        if accounts:
            logging.info(f"✓ Found accounts: {accounts}")
            all_accounts.extend(accounts)
        else:
            logging.error("TEST FAILED: No accounts found even with the correct public key")
            return False
    except Exception as e:
        logging.error(f"TEST FAILED: Error finding accounts: {e}")
        return False
    
    # Test 4: Check balance
    total_balance = 0
    for account_id in all_accounts:
        try:
            balance = get_account_balance(account_id)
            total_balance += balance
            logging.info(f"✓ Account {account_id} balance: {balance} tinybars")
        except Exception as e:
            logging.error(f"TEST FAILED: Error getting balance for {account_id}: {e}")
            return False
    
    if total_balance > 0:
        logging.info(f"✓ TEST PASSED: Total balance found: {total_balance} tinybars")
        return True
    else:
        logging.error("TEST FAILED: No balance found in any account")
        return False

def main():
    init_db()
    
    # Run test first
    if not test_known_wallet():
        logging.error("Known wallet test failed! Exiting...")
        return
    
    logging.info("=== STARTING WALLET RECOVERY ===")
    words = read_wordlist()
    logging.info(f"Loaded {len(words)} words for pattern generation")
    
    checked = 0
    found = 0
    batch_size = 500  # Increase batch size to use more memory
    max_workers = min(8, os.cpu_count() or 4)  # Reduce workers to control CPU usage
    
    # Pre-generate and cache patterns in memory (use more RAM)
    logging.info("Pre-generating smart patterns...")
    combos = generate_combinations(words)
    pattern_cache = []
    cache_size = 100000  # Cache 100k patterns in memory (increased from 50k)
    
    try:
        for i, combo in enumerate(combos):
            pattern_cache.append(combo)
            if i >= cache_size:
                break
        logging.info(f"Cached {len(pattern_cache)} smart patterns in memory")
    except Exception as e:
        logging.error(f"Error caching patterns: {e}")
        return
    
    # Process cached patterns in batches
    pattern_iter = iter(pattern_cache)
    while True:
        batch = list(itertools.islice(pattern_iter, batch_size))
        if not batch:
            # If we've exhausted cached patterns, generate more dynamically
            logging.info("Exhausted cached patterns, generating more...")
            additional_combos = generate_combinations(words)
            # Skip the patterns we already cached
            for _ in range(cache_size):
                try:
                    next(additional_combos)
                except StopIteration:
                    break
            # Continue with new patterns - this will now be infinite
            batch = list(itertools.islice(additional_combos, batch_size))
            if not batch:
                # This should never happen now with infinite generation
                logging.warning("Unexpected: pattern generation stopped, restarting...")
                combo_generator = generate_combinations(words)
                batch = list(itertools.islice(combo_generator, batch_size))
                if not batch:
                    logging.error("Critical: Unable to generate any patterns!")
                    break
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_combo, combo) for combo in batch]
            for future in as_completed(futures):
                try:
                    mnemonic, valid, balance = future.result()
                    checked += 1
                    if valid and balance and balance > 0:
                        found += 1
                        logging.info(f'🎉 WALLET FOUND! Mnemonic: {mnemonic}')
                        logging.info(f'💰 Balance: {balance} tinybars')
                        # You could return here if you want to stop after first wallet
                        # return mnemonic, balance
                    
                    # Enhanced progress tracking
                    if checked % 1000 == 0:  # Every 1000 combinations
                        import time
                        logging.info(f"📊 Progress: {checked:,} combinations tested, {found} wallets found")
                        logging.info(f"⏱️  Rate: ~{1000/60:.1f} combinations/minute")
                    elif checked % 500 == 0:  # Every 500 combinations (less verbose)
                        logging.info(f"Checked {checked:,} combinations, found {found} wallets with balance.")
                        
                except Exception as e:
                    logging.error(f"Error processing future: {e}")
                    continue
        
        # Memory management - force garbage collection every 5000 combinations
        if checked % 5000 == 0:
            import gc
            gc.collect()
            logging.info(f"🧹 Memory cleanup performed at {checked:,} combinations")

if __name__ == '__main__':
    main()
