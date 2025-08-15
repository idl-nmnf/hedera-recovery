# 🔐 Hedera Wallet Recovery Tool

A sophisticated, containerized brute-force recovery tool for Hedera (HBAR) wallets. This tool systematically generates and tests mnemonic combinations using advanced pattern recognition to recover lost wallets.

## 🌟 Features

### 🚀 **Advanced Pattern Generation**
- **14+ Smart Patterns**: Sliding windows, interleaved patterns, chunk-based distribution, Fibonacci sequences, prime number selection
- **Infinite Generation**: Truly infinite combination generation with multiple strategies
- **Memory Optimization**: Intelligent caching of 100,000+ patterns in RAM for optimal performance

### 🔧 **Multi-Wallet Derivation Support**
- **47+ Derivation Methods**: Supports all major wallet types and derivation standards
- **Ledger Hardware Wallets**: Specialized derivation methods for Ledger devices
- **HashPack Browser Wallets**: Custom derivation paths for HashPack extension
- **MetaMask, Blade, and other wallets**: Comprehensive wallet compatibility
- **BIP32/SLIP-10 Standards**: Full support for standard derivation methods

### ⚡ **High-Performance Architecture**
- **Docker Containerized**: Consistent environment across all platforms
- **Multi-threaded Processing**: Parallel processing with configurable worker threads
- **PostgreSQL Persistence**: Database storage for tracking progress and results
- **Memory Management**: Automatic garbage collection and memory optimization
- **Rate Limiting**: CPU usage control to maintain system stability

### 🔍 **Intelligent Recovery**
- **Hedera Mirror Node Integration**: Real-time balance checking via official API
- **Account Discovery**: Automatic detection of associated Hedera accounts
- **Balance Verification**: Only reports wallets with actual HBAR balances
- **Progress Tracking**: Detailed logging with combination testing rates

### 🛡️ **Security & Reliability**
- **Test Framework**: Built-in validation with known wallet testing
- **Error Recovery**: Robust error handling and automatic restart capabilities
- **Secure Storage**: Local processing with no external data transmission
- **Gitignore Protection**: Automatic protection of sensitive mnemonic files

## 📋 Prerequisites

- **Docker & Docker Compose**: For containerized deployment
- **Windows PowerShell**: Compatible with Windows environments
- **Memory**: Minimum 4GB RAM recommended for optimal performance
- **Storage**: At least 1GB free space for database and logs

## 🚀 Quick Start

### 1. **Setup Your Word List**
Create `data/wordlist.txt` with your suspected mnemonic words:
```
abandon
ability
about
above
...your suspected words...
```

### 2. **Test with Known Wallet (Optional)**
Create `data/test_mnemonic.txt` with a known wallet for validation:
```
word1 word2 word3 ... word24
```

### 3. **Build and Run**
```powershell
# Build the application
docker compose build

# Test with known wallet (if you have one)
docker compose run --rm app python main.py --test

# Start the recovery process
docker compose up
```

## 🔧 Configuration

### **Environment Variables**
```yaml
# docker-compose.yml
environment:
  - DB_HOST=db
  - DB_USER=hedera
  - DB_PASSWORD=recovery
  - DB_NAME=hedera_recovery
```

### **Performance Tuning**
- **Max Workers**: Automatically configured based on CPU cores
- **Batch Size**: 500 combinations per batch (configurable)
- **Cache Size**: 100,000 patterns cached in memory
- **Rate Limiting**: CPU usage maintained below 90%

## 📊 Pattern Generation Strategies

### **Smart Patterns (High Priority)**
1. **Exact Match**: Uses wordlist as-is if exactly 24 words
2. **Sliding Windows**: Overlapping sequences from wordlist
3. **Split Patterns**: First N + Last N word combinations
4. **Interleaved**: Every Nth word selection
5. **Chunk-based**: Distributed selection across word groups

### **Mathematical Patterns**
6. **Fibonacci Selection**: Words selected using Fibonacci sequence
7. **Prime Number**: Selection based on prime number positions
8. **Random Sampling**: Multiple deterministic random seeds

### **Infinite Generation**
9. **Advanced Random**: Infinite random pattern generation
10. **Systematic Combinations**: All possible combinations with repetition
11. **Permutations**: All possible word orderings
12. **Combinations**: All possible selections without repetition

## 🔐 Supported Wallet Types

### **Hardware Wallets**
- ✅ **Ledger Nano S/X**: Specialized Ledger derivation methods
- ✅ **Other Hardware**: Standard BIP32/SLIP-10 support

### **Software Wallets**
- ✅ **HashPack**: Browser extension with custom derivation paths
- ✅ **MetaMask**: Web3-compatible derivation
- ✅ **Blade Wallet**: Hedera-specific mobile wallet
- ✅ **Standard BIP39**: All standard mnemonic wallets

### **Derivation Methods**
- **47+ Methods**: Comprehensive coverage of all known derivation standards
- **Real-time Testing**: Each mnemonic tested against all methods
- **Automatic Detection**: No need to specify wallet type

## 📈 Performance Metrics

### **Testing Rates**
- **~1000 combinations/minute**: Typical processing rate
- **47+ derivations per combination**: Comprehensive testing
- **Parallel Processing**: 6-8 worker threads maximum

### **Memory Usage**
- **Base**: ~500MB container overhead
- **Cache**: ~100MB for 100,000 cached patterns
- **Peak**: ~1GB during intensive processing

### **Network Usage**
- **Minimal**: Only Hedera Mirror Node API calls for balance checking
- **Rate Limited**: Respects API rate limits
- **Efficient**: Cached results to minimize redundant calls

## 📝 Output & Logging

### **Progress Tracking**
```
📊 Progress: 15,000 combinations tested, 0 wallets found
⏱️  Rate: ~16.7 combinations/minute
🧹 Memory cleanup performed at 15,000 combinations
```

### **Wallet Discovery**
```
🎉 WALLET FOUND! Mnemonic: word1 word2 word3 ... word24
💰 Balance: 8666100000 tinybars
✓ Account: 0.0.9612968
```

### **Database Storage**
- **Progress Persistence**: All tested combinations stored
- **Resume Capability**: Can resume from interruptions
- **Result History**: Complete audit trail of recovery attempts

## 🛠️ Troubleshooting

### **Common Issues**

**"All patterns exhausted!"**
- ✅ **Fixed**: This issue has been resolved with infinite pattern generation
- The tool now continues indefinitely with systematic enumeration

**Memory Issues**
- Reduce `cache_size` in main.py
- Increase Docker memory allocation
- Monitor system resources

**API Rate Limiting**
- Tool automatically handles Hedera API rate limits
- Implements exponential backoff for reliability

**Database Connection**
- Ensure PostgreSQL container is healthy
- Check Docker network connectivity
- Verify environment variables

### **Performance Optimization**

**Increase Processing Speed**
- Add more CPU cores to Docker
- Increase `max_workers` (careful with API limits)
- Use SSD storage for database

**Reduce Memory Usage**
- Decrease `cache_size` from 100,000
- Lower `batch_size` from 500
- Enable more frequent garbage collection

## 📋 Technical Architecture

### **Container Architecture**
```
┌─────────────────┐    ┌──────────────────┐
│   Application   │    │   PostgreSQL     │
│   Container     │◄──►│   Database       │
│   (Python)      │    │   Container      │
└─────────────────┘    └──────────────────┘
        │
        ▼
┌─────────────────┐
│   Hedera        │
│   Mirror Node   │
│   (API)         │
└─────────────────┘
```

### **Processing Flow**
1. **Pattern Generation**: Smart algorithms generate mnemonic combinations
2. **Derivation Testing**: Each combination tested against 47+ methods
3. **Public Key Generation**: Cryptographic derivation of public keys
4. **Account Lookup**: Hedera API queries for associated accounts
5. **Balance Verification**: Balance checking for discovered accounts
6. **Result Storage**: Database persistence of all results

### **Technologies Used**
- **Python 3.11**: Core application language
- **Docker Compose**: Container orchestration
- **PostgreSQL 15**: Data persistence
- **Cryptography Library**: Ed25519 key derivation
- **BIP32/SLIP-10**: Standard derivation protocols
- **Hedera Mirror Node**: Official Hedera network API

## ⚠️ Important Notes

### **Security Considerations**
- **Local Processing**: All computation happens locally
- **No External Transmission**: Mnemonics never leave your system
- **Secure Storage**: Use `.gitignore` for sensitive files
- **Test Environment**: Always test with known wallets first

### **Legal & Ethical Use**
- **Own Wallets Only**: Only use for recovering your own lost wallets
- **Legal Compliance**: Ensure compliance with local regulations
- **Responsible Use**: This tool is for legitimate recovery purposes only

### **Recovery Expectations**
- **Time Investment**: Recovery can take significant time
- **Success Rate**: Depends on word list accuracy and completeness
- **Resource Usage**: High CPU and memory usage during operation
- **Patience Required**: Systematic recovery is a methodical process

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional wallet derivation methods
- Performance optimizations
- Pattern generation algorithms
- Documentation improvements

## 📄 License

This project is for educational and legitimate wallet recovery purposes only. Use responsibly and in accordance with applicable laws.

---

**⚡ Happy Recovery!** 🔐💎
