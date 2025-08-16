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


def read_test_mnemonics():
    """Read test mnemonics from file (supports multiple lines)."""
    try:
        with open(TEST_MNEMONIC_PATH, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
        return lines
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading test mnemonics: {e}")
        return []


def read_expected_keys():
    """Read expected keys for testing (supports multiple lines)."""
    try:
        with open(TEST_EXPECTED_KEY_PATH, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
        return lines
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading expected keys: {e}")
        return []


def read_test_mnemonic():
    """Read test mnemonic if available (legacy single-line support)."""
    mnemonics = read_test_mnemonics()
    return mnemonics[0] if mnemonics else None


def read_expected_key():
    """Read expected key for testing (legacy single-line support)."""
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
                device_info = gpu_accelerator.get_device_info()
                if device_info.get('available', False):
                    print(f"✅ GPU acceleration enabled: {device_info}")
                else:
                    print(f"⚠️ GPU detected but not available for acceleration: {device_info}")
                    print("ℹ️ This is normal in Docker without GPU drivers")
            except Exception as e:
                print(f"⚠️ GPU acceleration failed to initialize: {e}")
                print("ℹ️ Continuing with CPU-only processing")
        else:
            print("ℹ️ GPU acceleration disabled in configuration")
        
        # Display system capabilities
        print(f"💻 System: {performance_monitor.get_system_info()}")
        print("🚀 High-performance recovery system ready!")
    
    # Initialize recovery engine
    engine = RecoveryEngine()
    engine.initialize()
    
    try:
        # Check command line arguments
        test_mode = '--test' in sys.argv
        
        if test_mode:
            # Test mode with multiple known wallets
            test_mnemonics = read_test_mnemonics()
            expected_keys = read_expected_keys()
            
            if not test_mnemonics:
                print(f"Error: {TEST_MNEMONIC_PATH} not found for testing.")
                print("Create this file with known 24-word mnemonics for validation (one per line).")
                sys.exit(1)
            
            print(f"🧪 Testing {len(test_mnemonics)} known wallet(s)...")
            
            # Test each wallet
            all_passed = True
            for i, test_mnemonic in enumerate(test_mnemonics, 1):
                print(f"\n📋 Testing wallet #{i}: {test_mnemonic[:20]}...")
                
                # Use corresponding expected key if available, otherwise test without validation
                expected_key = expected_keys[i-1] if i <= len(expected_keys) else None
                
                if expected_key:
                    print(f"🔑 Expected key: {expected_key}")
                    success = engine.test_known_wallet(test_mnemonic, expected_key)
                    if success:
                        print(f"✅ Wallet #{i} test PASSED!")
                    else:
                        print(f"❌ Wallet #{i} test FAILED!")
                        all_passed = False
                else:
                    print(f"⚠️ No expected key for wallet #{i}, testing derivation methods only...")
                    # Test derivation without key validation (just show what methods produce keys)
                    success = engine.test_derivation_methods(test_mnemonic)
                    if success:
                        print(f"✅ Wallet #{i} derivation test completed!")
                    else:
                        print(f"❌ Wallet #{i} derivation test failed!")
                        all_passed = False
            
            if all_passed:
                print(f"\n🎉 All {len(test_mnemonics)} wallet tests PASSED!")
                print("✅ Recovery system is working correctly for all test cases.")
            else:
                print(f"\n⚠️ Some wallet tests failed. Please check your derivation methods.")
                sys.exit(1)
                
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
