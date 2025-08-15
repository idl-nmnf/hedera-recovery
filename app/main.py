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
    for _ in range(min(10000, word_count * 10)):  # Use more memory for caching
        if word_count >= length:
            sampled_indices = random.sample(word_indices, length)
            pattern = tuple(words[i] for i in sampled_indices)
            cached_patterns.append(pattern)
    
    # Yield cached patterns
    for pattern in cached_patterns:
        yield pattern
    
    # Pattern 7: Finally, if nothing else works, do systematic combinations
    # (This is the expensive fallback)
    if word_count < length:
        for combo in itertools.product(words, repeat=length):
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
    # Hedera uses Ed25519 keys, return raw public key as hex for Mirror Node API
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except ImportError:
        raise ImportError("Please add 'cryptography' to requirements.txt")
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed[:32])
    public_key = private_key.public_key()
    pubkey_raw = public_key.public_bytes_raw()
    pubkey_hex = pubkey_raw.hex()
    return pubkey_hex

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
        pubkey_hex = mnemonic_to_public_key(mnemonic)
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
    
    logging.info("=== TESTING KNOWN WALLET ===")
    logging.info(f"Testing mnemonic from test_mnemonic.txt")
    
    # Test 1: Check if mnemonic is valid
    if not is_valid_mnemonic(test_mnemonic):
        logging.error("TEST FAILED: Mnemonic is not valid BIP39")
        return False
    logging.info("✓ Mnemonic is valid BIP39")
    
    # Test 2: Derive public key
    try:
        pubkey_hex = mnemonic_to_public_key(test_mnemonic)
        logging.info(f"✓ Derived public key: {pubkey_hex}")
    except Exception as e:
        logging.error(f"TEST FAILED: Could not derive public key: {e}")
        return False
    
    # Test 3: Find accounts
    try:
        accounts = find_accounts_by_public_key(pubkey_hex)
        if not accounts:
            logging.error("TEST FAILED: No accounts found for this public key")
            return False
        logging.info(f"✓ Found accounts: {accounts}")
    except Exception as e:
        logging.error(f"TEST FAILED: Error finding accounts: {e}")
        return False
    
    # Test 4: Check balance
    total_balance = 0
    for account_id in accounts:
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
    cache_size = 50000  # Cache 50k patterns in memory
    
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
            # Continue with new patterns
            batch = list(itertools.islice(additional_combos, batch_size))
            if not batch:
                logging.info("All patterns exhausted!")
                break
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_combo, combo) for combo in batch]
            for future in as_completed(futures):
                try:
                    mnemonic, valid, balance = future.result()
                    checked += 1
                    if valid and balance and balance > 0:
                        found += 1
                        logging.info(f'🎉 Found wallet: {mnemonic} with balance {balance} tinybars')
                    if checked % 500 == 0:  # Log every 500 instead of 100
                        logging.info(f"Checked {checked} combinations, found {found} wallets with balance.")
                except Exception as e:
                    logging.error(f"Error processing future: {e}")
                    continue

if __name__ == '__main__':
    main()
