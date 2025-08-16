"""Configuration settings for Hedera wallet recovery tool - Optimized for high-performance systems."""

import os
from pathlib import Path

# =============================================================================
# SYSTEM SPECIFICATIONS AUTO-DETECTION
# =============================================================================

def load_system_specs():
    """Load system specifications from TOML file."""
    try:
        import toml
        # Try to load from app directory first, then parent directory
        specs_file = Path(__file__).parent / "system_specs.toml"
        if not specs_file.exists():
            specs_file = Path(__file__).parent.parent / "system_specs.toml"
        
        if specs_file.exists():
            specs = toml.load(specs_file)
            print(f"✅ System specs loaded from: {specs_file}")
            return specs
        else:
            print("⚠️ system_specs.toml not found - using defaults")
    except ImportError:
        print("⚠️ TOML library not available - using default configuration")
    except Exception as e:
        print(f"⚠️ Could not load system specs: {e}")
    return {}

SYSTEM_SPECS = load_system_specs()

def get_cpu_threads():
    """Get CPU thread count from specs or system."""
    if 'cpu' in SYSTEM_SPECS:
        return SYSTEM_SPECS['cpu'].get('threads', 12)
    return os.cpu_count() or 12

def get_memory_gb():
    """Get total memory in GB."""
    if 'memory' in SYSTEM_SPECS:
        ram_str = SYSTEM_SPECS['memory'].get('total_ram', '32GB')
        return int(ram_str.replace('GB', ''))
    return 16  # Conservative fallback

def has_gpu_compute():
    """Check if GPU compute acceleration is available."""
    if 'gpu' in SYSTEM_SPECS:
        return SYSTEM_SPECS['gpu'].get('compute_capable', False)
    return False

# =============================================================================
# ADAPTIVE PERFORMANCE CONFIGURATION
# =============================================================================

# System capabilities
CPU_THREADS = get_cpu_threads()  # 12 threads for i5-11400F
MEMORY_GB = get_memory_gb()      # 32GB RAM
HAS_GPU = has_gpu_compute()      # AMD RX 6600

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'hedera')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'recovery')
DB_NAME = os.getenv('DB_NAME', 'hedera_recovery')

# File paths
WORDLIST_PATH = 'wordlist.txt'
TEST_MNEMONIC_PATH = 'test_mnemonic.txt'
TEST_EXPECTED_KEY_PATH = 'test_expected_key.txt'

# Performance settings
DEFAULT_BATCH_SIZE = 15000                                 # Massive batches
DEFAULT_CACHE_SIZE = 5000000                               # 5M pattern cache
MAX_WORKERS = 20                                           # Aggressive threading

# Memory optimization settings
MEMORY_CACHE_SIZE = 8 * 1024 * 1024 * 1024                # 8GB RAM cache
DISK_CACHE_SIZE = 50 * 1024 * 1024 * 1024                 # 50GB SSD cache
PREFETCH_BUFFER_SIZE = 50000                               # 50K pattern prefetch

# GPU acceleration settings
ENABLE_GPU_ACCELERATION = HAS_GPU
GPU_BATCH_SIZE = 2000 if HAS_GPU else 0
GPU_MEMORY_LIMIT = 6 * 1024 * 1024 * 1024 if HAS_GPU else 0  # 6GB GPU memory limit

# Advanced processing settings
PARALLEL_DERIVATION = True                                 # Parallel key derivation
ASYNC_API_CALLS = True                                     # Async Hedera API calls
ENABLE_PATTERN_CACHING = True                              # Cache generated patterns
ENABLE_RESULT_BATCHING = True                              # Batch database operations

# Recovery settings - MAXIMUM THROUGHPUT MODE
MNEMONIC_LENGTH = 24
PROGRESS_LOG_INTERVAL = 25000                              # Log every 25K combinations (reduce logging overhead)
BATCH_LOG_INTERVAL = 15000                                 # Larger batch processing logs
MEMORY_CLEANUP_INTERVAL = 100000                           # Less frequent cleanup (higher memory usage)
DATABASE_BATCH_COMMIT = 5000                               # Larger batch commits (more throughput)

# Hedera API settings - AGGRESSIVE API ACCESS
HEDERA_MAINNET_URL = "https://mainnet-public.mirrornode.hedera.com/api/v1"
API_TIMEOUT = 15                                           # Faster timeout for speed
MAX_CONCURRENT_API_CALLS = 50                              # MASSIVE concurrent requests
API_RETRY_ATTEMPTS = 3                                     # Fewer retries for speed
API_RETRY_DELAY = 1                                        # Shorter retry delay
API_RATE_LIMIT = 200                                       # Double the request rate

# System monitoring - Reduced monitoring overhead
ENABLE_PERFORMANCE_MONITORING = True
PERFORMANCE_LOG_INTERVAL = 60                              # Less frequent monitoring (reduce overhead)
CPU_USAGE_THRESHOLD = 95                                   # Alert if CPU > 95%
MEMORY_USAGE_THRESHOLD = 85                                # Alert if memory > 85%

print(f"🚀 High-Performance Configuration Loaded")
print(f"💻 System: {SYSTEM_SPECS.get('system', {}).get('name', 'Unknown System')}")
print(f"🔧 CPU: {CPU_THREADS} threads, RAM: {MEMORY_GB}GB, GPU: {'Enabled' if HAS_GPU else 'Disabled'}")
print(f"⚡ Optimized: Batch={DEFAULT_BATCH_SIZE}, Cache={DEFAULT_CACHE_SIZE}, Workers={MAX_WORKERS}")
