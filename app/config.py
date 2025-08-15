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

# Performance settings
DEFAULT_BATCH_SIZE = 500
DEFAULT_CACHE_SIZE = 100000
MAX_WORKERS = min(8, os.cpu_count() or 4)

# Recovery settings
MNEMONIC_LENGTH = 24
PROGRESS_LOG_INTERVAL = 1000
BATCH_LOG_INTERVAL = 500
MEMORY_CLEANUP_INTERVAL = 5000

# Hedera API settings
HEDERA_MAINNET_URL = "https://mainnet-public.mirrornode.hedera.com/api/v1"
API_TIMEOUT = 10
