# Copilot Instructions: Hedera Wallet Recovery Tool

## Design Choices
- **Language:** Python (best for scripting, crypto, Docker)
- **Database:** PostgreSQL (stores combinations, results, persistent)
- **Containers:** All components run in Docker for reliability

## Main Logic
1. Read word list from file or DB
2. Generate combinations (start with common, then brute-force)
3. For each combination:
   - Check if valid Hedera mnemonic
   - If valid, check wallet balance
   - Store combination and result in DB
4. On restart, resume from last state (query DB for progress)

## Database Schema
- `combinations` table: stores mnemonic, checked status, balance found

## Future Agent Guidance
- Use Python's multiprocessing for speed
- Consider distributed approaches for scale
- Add web dashboard for monitoring
- Use Hedera SDK for wallet/mnemonic validation

## Extending
- Add new word sources by updating `data/wordlist.txt` or DB
- Tune brute-force logic in `app/main.py`
- Update Docker Compose for new services

## Security
- Never expose DB or app ports publicly
- Store sensitive results securely

## References
- [Hedera SDK](https://github.com/hashgraph/hedera-sdk-python)
- [BIP39 Mnemonic](https://github.com/trezor/python-mnemonic)
