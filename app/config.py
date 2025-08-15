"""Configuration settings for Hedera wallet recovery tool."""

import os

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'hedera')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'recovery')
DB_NAME = os.getenv('DB_NAME', 'hedera_recovery')

# File paths
WORDLIST_PATH = 'wordlist.txt'
TEST_MNEMONIC_PATH = 'test_mnemonic.txt'
TEST_EXPECTED_KEY_PATH = 'test_expected_key.txt'
EXPECTED_KEY_PATH = 'expected_key.txt'

# Performance settings
DEFAULT_BATCH_SIZE = 1000
DEFAULT_CACHE_SIZE = 250000
MAX_WORKERS = min(6, os.cpu_count() or 4)

# Recovery settings
MNEMONIC_LENGTH = 24
PROGRESS_LOG_INTERVAL = 2000
BATCH_LOG_INTERVAL = 1000
MEMORY_CLEANUP_INTERVAL = 7500

# Hedera API settings - Optimized for faster requests
HEDERA_MAINNET_URL = "https://mainnet-public.mirrornode.hedera.com/api/v1"
API_TIMEOUT = 15                    # Increased timeout for stability under higher load
MAX_CONCURRENT_API_CALLS = 10       # Limit concurrent API calls to avoid rate limiting
API_RETRY_ATTEMPTS = 3              # Retry failed API calls
API_RETRY_DELAY = 1                 # Delay between retries (seconds)
