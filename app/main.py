"""
Hedera Wallet Recovery Tool - Main Entry Point

A sophisticated tool for recovering lost Hedera wallets using advanced pattern recognition
and comprehensive derivation method testing.
"""

import sys
import os
from recovery import RecoveryEngine
from config import WORDLIST_PATH, TEST_MNEMONIC_PATH, TEST_EXPECTED_KEY_PATH, has_gpu_compute

# Import high-performance modules
try:
    from performance_monitor import PerformanceMonitor
    from gpu_acceleration import GPUAccelerator
    PERFORMANCE_ENABLED = True
except ImportError as e:
    print(f"⚠️ Performance modules not available: {e}")
    PERFORMANCE_ENABLED = False


def read_wordlist():
    """Read wordlist from file."""
    try:
        with open(WORDLIST_PATH, 'r') as f:
            words = [w.strip() for w in f if w.strip() and not w.startswith('#')]
        return words
    except FileNotFoundError:
        print(f"Error: {WORDLIST_PATH} not found. Please create it with your suspected mnemonic words.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading wordlist: {e}")
        sys.exit(1)


def read_test_mnemonic():
    """Read test mnemonic if available."""
    try:
        with open(TEST_MNEMONIC_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading test mnemonic: {e}")
        return None


def read_expected_key():
    """Read expected key for testing."""
    try:
        with open(TEST_EXPECTED_KEY_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading expected key: {e}")
        return None


def main():
    """Main application entry point."""
    # Initialize performance monitoring if available
    performance_monitor = None
    gpu_accelerator = None
    
    if PERFORMANCE_ENABLED:
        print("🚀 Initializing high-performance system...")
        performance_monitor = PerformanceMonitor()
        performance_monitor.start_monitoring()
        
        if has_gpu_compute():
            print("🎯 Initializing GPU acceleration...")
            try:
                gpu_accelerator = GPUAccelerator()
                print(f"✅ GPU acceleration enabled: {gpu_accelerator.get_device_info()}")
            except Exception as e:
                print(f"⚠️ GPU acceleration failed to initialize: {e}")
        
        # Display system capabilities
        print(f"💻 System: {performance_monitor.get_system_info()}")
    
    # Initialize recovery engine
    engine = RecoveryEngine()
    engine.initialize()
    
    try:
        # Check command line arguments
        test_mode = '--test' in sys.argv
        
        if test_mode:
            # Test mode with known wallet
            test_mnemonic = read_test_mnemonic()
            if not test_mnemonic:
                print(f"Error: {TEST_MNEMONIC_PATH} not found for testing.")
                print("Create this file with a known 24-word mnemonic for validation.")
                sys.exit(1)
            
            # Read expected key from file
            expected_key = read_expected_key()
            if not expected_key:
                print(f"Error: {TEST_EXPECTED_KEY_PATH} not found for testing.")
                print("Create this file with the expected private key for validation.")
                sys.exit(1)
            
            success = engine.test_known_wallet(test_mnemonic, expected_key)
            if not success:
                print("❌ Known wallet test failed! Please check your derivation methods.")
                sys.exit(1)
            
            print("✅ Test passed! Recovery system is working correctly.")
            sys.exit(0)
        
        else:
            # Recovery mode
            words = read_wordlist()
            
            if len(words) < 12:
                print("Warning: Wordlist seems small. Consider adding more suspected words.")
            
            print(f"Starting recovery with {len(words)} words...")
            print("This process will run indefinitely until a wallet is found.")
            print("Press Ctrl+C to stop.")
            
            try:
                result = engine.run_recovery(words)
                
                if result:
                    mnemonic, balance = result
                    print(f"\n🎉 SUCCESS! Wallet recovered!")
                    print(f"💰 Mnemonic: {mnemonic}")
                    print(f"💰 Balance: {balance} tinybars")
                else:
                    print("Recovery process completed without finding a wallet.")
            
            except KeyboardInterrupt:
                print("\n⏹️ Recovery stopped by user.")
                stats = engine.database.get_stats()
                print(f"📊 Final stats: {stats['total_tested']:,} combinations tested, {stats['wallets_found']} wallets found")
            
            except Exception as e:
                print(f"❌ Recovery failed with error: {e}")
                sys.exit(1)
    
    finally:
        # Cleanup performance monitoring
        if performance_monitor:
            performance_monitor.stop_monitoring()
            print(f"📈 Final performance metrics: {performance_monitor.get_metrics()}")


if __name__ == '__main__':
    main()
