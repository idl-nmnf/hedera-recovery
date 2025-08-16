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

# Performance settings - Optimized for your powerful hardware
DEFAULT_BATCH_SIZE = min(5000, MEMORY_GB * 150)           # 4800 for 32GB system
DEFAULT_CACHE_SIZE = min(2000000, MEMORY_GB * 50000)      # 1.6M for 32GB system  
MAX_WORKERS = min(CPU_THREADS - 1, 11)                    # 11 workers (leave 1 for system)

# Memory optimization settings
MEMORY_CACHE_SIZE = MEMORY_GB * 64 * 1024 * 1024          # 2GB cache for 32GB system
DISK_CACHE_SIZE = 20 * 1024 * 1024 * 1024                 # 20GB NVMe SSD cache
PREFETCH_BUFFER_SIZE = 10000                               # Prefetch 10K patterns

# GPU acceleration settings
ENABLE_GPU_ACCELERATION = HAS_GPU
GPU_BATCH_SIZE = 2000 if HAS_GPU else 0
GPU_MEMORY_LIMIT = 6 * 1024 * 1024 * 1024 if HAS_GPU else 0  # 6GB GPU memory limit

# Advanced processing settings
PARALLEL_DERIVATION = True                                 # Parallel key derivation
ASYNC_API_CALLS = True                                     # Async Hedera API calls
ENABLE_PATTERN_CACHING = True                              # Cache generated patterns
ENABLE_RESULT_BATCHING = True                              # Batch database operations

# Recovery settings - Optimized for high throughput
MNEMONIC_LENGTH = 24
PROGRESS_LOG_INTERVAL = 10000                              # Log every 10K combinations
BATCH_LOG_INTERVAL = 5000                                  # Batch processing logs
MEMORY_CLEANUP_INTERVAL = 50000                            # Cleanup every 50K combinations
DATABASE_BATCH_COMMIT = 2000                               # Batch commit size

# Hedera API settings - Optimized for high-performance access
HEDERA_MAINNET_URL = "https://mainnet-public.mirrornode.hedera.com/api/v1"
API_TIMEOUT = 25                                           # Increased timeout for stability
MAX_CONCURRENT_API_CALLS = 20                              # More concurrent requests
API_RETRY_ATTEMPTS = 5                                     # More retries
API_RETRY_DELAY = 2                                        # Longer retry delay
API_RATE_LIMIT = 100                                       # Requests per second limit

# System monitoring
ENABLE_PERFORMANCE_MONITORING = True
PERFORMANCE_LOG_INTERVAL = 30                              # Log performance every 30 seconds
CPU_USAGE_THRESHOLD = 95                                   # Alert if CPU > 95%
MEMORY_USAGE_THRESHOLD = 85                                # Alert if memory > 85%

print(f"🚀 High-Performance Configuration Loaded")
print(f"💻 System: {SYSTEM_SPECS.get('system', {}).get('name', 'Unknown System')}")
print(f"🔧 CPU: {CPU_THREADS} threads, RAM: {MEMORY_GB}GB, GPU: {'Enabled' if HAS_GPU else 'Disabled'}")
print(f"⚡ Optimized: Batch={DEFAULT_BATCH_SIZE}, Cache={DEFAULT_CACHE_SIZE}, Workers={MAX_WORKERS}")
