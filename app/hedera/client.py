"""Hedera network API client for account and balance operations."""

import requests
import logging
from typing import List, Optional
from config import HEDERA_MAINNET_URL, API_TIMEOUT


class HederaClient:
    """Client for interacting with Hedera Mirror Node API."""
    
    def __init__(self):
        self.base_url = HEDERA_MAINNET_URL
        self.timeout = API_TIMEOUT
    
    def find_accounts_by_public_key(self, pubkey_hex: str) -> List[str]:
        """Find Hedera accounts associated with a public key."""
        url = f"{self.base_url}/accounts?account.publickey={pubkey_hex}"
        
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            accounts = [a['account'] for a in data.get('accounts', [])]
            return accounts
        except Exception as e:
            logging.error(f"Error finding accounts for pubkey {pubkey_hex}: {e}")
            return []
    
    def get_account_balance(self, account_id: str) -> int:
        """Get the balance of a Hedera account in tinybars."""
        url = f"{self.base_url}/accounts/{account_id}"
        
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get('balance', {}).get('balance', 0)
        except Exception as e:
            logging.error(f"Error getting balance for account {account_id}: {e}")
            return 0
    
    def check_balance_for_keys(self, derivation_methods: List[tuple]) -> tuple:
        """Check balances for all derived keys and return first wallet with balance."""
        for method_name, pubkey_hex in derivation_methods:
            if not pubkey_hex:
                continue
                
            accounts = self.find_accounts_by_public_key(pubkey_hex)
            if accounts:
                total_balance = 0
                for account_id in accounts:
                    balance = self.get_account_balance(account_id)
                    total_balance += balance
                
                if total_balance > 0:
                    logging.info(f"✓ Found wallet with method: {method_name}")
                    logging.info(f"✓ Accounts: {accounts}")
                    logging.info(f"✓ Total balance: {total_balance} tinybars")
                    return method_name, accounts, total_balance
        
        return None, [], 0
