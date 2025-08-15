# Hedera Wallet Recovery Brute-Force Tool

This project attempts to recover a Hedera (HBAR) wallet by generating and testing infinite word combinations as possible mnemonic phrases. It checks each combination for validity and wallet balance, storing results to avoid repeats. All components run in Docker containers for reliability and persistence.

## Features
- **Smart Pattern Recognition**: Advanced 24-word mnemonic generation using multiple heuristic patterns
- **Memory-Optimized Processing**: Caches up to 50,000 patterns in RAM for faster access
- **Intelligent Combination Generation**:
  - Sliding window patterns from wordlist
  - Split patterns (first N + last N words)
  - Interleaved patterns (every Nth word)
  - Chunk-based sampling from wordlist sections
  - Deterministic random sampling with caching
  - Reverse order testing for all patterns
- Checks for valid Hedera wallet and balance using mainnet Mirror Node API
- Stores all tried combinations and results in PostgreSQL
- Resumes from last state on restart
- Multi-threaded processing optimized for CPU/memory balance
- Built-in testing with known wallet validation
- Error recovery (retries failed checks)

## Setup
1. Install Docker & Docker Compose
2. Clone this repo
3. Place your word list in `data/wordlist.txt`
4. Create `data/test_mnemonic.txt` with a known valid mnemonic for testing
5. Run: `docker compose up --build`

## Architecture
- **Python app**: Generates smart 24-word combinations using advanced pattern recognition
  - Ed25519 cryptography for key derivation
  - Memory-cached pattern generation (50k+ patterns in RAM)
  - CPU-optimized threading (6 workers max to stay under 90% CPU)
  - Batch processing (500 combinations per batch for memory efficiency)
- **PostgreSQL**: Stores tried combinations and results with health checks
- **Hedera Mirror Node**: Queries mainnet accounts and balances via REST API

## Usage
- All configuration is in `docker-compose.yml`
- Results are stored in the database
- Logs show progress and findings
- App automatically tests known wallet before starting recovery
- Failed checks are retried in future runs

## Security
- Sensitive files (`test_mnemonic.txt`, database) are excluded from version control
- Uses mainnet for real wallet detection
- Parallel processing with memory management

## Performance Optimization
- **CPU Management**: Limited to 6 worker threads to maintain <90% CPU usage
- **Memory Utilization**: Uses up to 45% memory with pattern caching and large batches
- **Smart Patterns**: Tests intelligent 24-word combinations instead of brute force
- **Progress Tracking**: Logs every 500 combinations to reduce overhead

## Files Structure
```
├── app/
│   ├── main.py          # Main recovery logic
│   ├── Dockerfile       # Python app container
│   └── requirements.txt # Python dependencies
├── data/
│   ├── wordlist.txt     # BIP39 word list
│   ├── test_mnemonic.txt # Known wallet for testing (gitignored)
│   └── db/              # PostgreSQL data (gitignored)
├── docker-compose.yml   # Container orchestration
├── .gitignore          # Security exclusions
└── README.md           # This file
```

## Future Improvements
- Web dashboard for monitoring
- ~~Advanced heuristics and pattern recognition~~ ✅ **IMPLEMENTED**
- Distributed processing across multiple machines
- Rate limiting for API calls
- Machine learning for pattern optimization

See `copilot-instructions.md` for technical details and agent guidance.
