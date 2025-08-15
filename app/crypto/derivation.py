"""Key derivation methods for various wallet types."""

import hashlib
import hmac
import itertools
from typing import List, Tuple
from mnemonic import Mnemonic
from cryptography.hazmat.primitives.asymmetric import ed25519


class KeyDerivation:
    """Handles all key derivation methods for different wallet types."""
    
    def __init__(self):
        self.mnemo = Mnemonic('english')
    
    def derive_all_keys(self, mnemonic: str) -> List[Tuple[str, str]]:
        """Derive public keys using all known methods."""
        derivation_methods = []
        
        try:
            # Validate mnemonic
            if not self.mnemo.check(mnemonic):
                return [("invalid_mnemonic", "")]
            
            seed = self.mnemo.to_seed(mnemonic)
            
            # Add all derivation methods
            derivation_methods.extend(self._basic_derivations(seed, mnemonic))
            derivation_methods.extend(self._pbkdf2_variations(mnemonic))
            derivation_methods.extend(self._bip32_accounts(seed))
            derivation_methods.extend(self._wallet_specific(seed))
            derivation_methods.extend(self._passphrase_variations(mnemonic))
            derivation_methods.extend(self._alternative_methods(seed, mnemonic))
            derivation_methods.extend(self._ledger_derivations(seed))
            derivation_methods.extend(self._hashpack_derivations(seed))
            derivation_methods.extend(self._advanced_methods(seed, mnemonic))
            
        except Exception as e:
            return [("error", f"Derivation failed: {e}")]
        
        return derivation_methods
    
    def _basic_derivations(self, seed: bytes, mnemonic: str) -> List[Tuple[str, str]]:
        """Basic derivation methods."""
        methods = []
        
        try:
            # Direct seed to private key
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed[:32])
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            methods.append(("direct_seed", pubkey_hex))
            
            # BIP32 Ed25519 standard derivation
            derived_key = self._bip32_ed25519_derive(seed, [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000])
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            methods.append(("bip32_ed25519", pubkey_hex))
            
        except Exception:
            pass
        
        return methods
    
    def _pbkdf2_variations(self, mnemonic: str) -> List[Tuple[str, str]]:
        """PBKDF2 variations with different salts."""
        methods = []
        
        pbkdf2_variants = [
            ("pbkdf2_hedera", b"mnemonic" + "hedera".encode(), 2048),
            ("pbkdf2_default", b"mnemonic", 2048),
            ("pbkdf2_bitcoin", b"mnemonic", 4096),
        ]
        
        for method_name, salt, iterations in pbkdf2_variants:
            try:
                import pbkdf2
                derived_seed = pbkdf2.PBKDF2(mnemonic, salt, iterations).read(32)
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_seed)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                methods.append((method_name, pubkey_hex))
            except:
                pass
        
        return methods
    
    def _bip32_accounts(self, seed: bytes) -> List[Tuple[str, str]]:
        """BIP32 account variations."""
        methods = []
        
        for account in range(10):
            try:
                path = [44 + 0x80000000, 3030 + 0x80000000, account + 0x80000000, 0 + 0x80000000, 0 + 0x80000000]
                derived_key = self._bip32_ed25519_derive(seed, path)
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                methods.append((f"bip32_account_{account}", pubkey_hex))
            except:
                pass
        
        return methods
    
    def _wallet_specific(self, seed: bytes) -> List[Tuple[str, str]]:
        """Wallet-specific derivation methods."""
        methods = []
        
        wallet_methods = [
            ("metamask_style", self._metamask_derivation),
            ("hashpack_style", self._hashpack_derivation),
            ("blade_style", self._blade_derivation),
            ("secp256k1_style", self._secp256k1_derivation),
        ]
        
        for method_name, derivation_func in wallet_methods:
            try:
                pubkey_hex = derivation_func(seed)
                if pubkey_hex:
                    methods.append((method_name, pubkey_hex))
            except:
                pass
        
        return methods
    
    def _passphrase_variations(self, mnemonic: str) -> List[Tuple[str, str]]:
        """Passphrase variations."""
        methods = []
        
        passphrases = ["", "hedera", "HEDERA", "Hedera", "hbar", "HBAR"]
        
        for passphrase in passphrases:
            try:
                seed = self.mnemo.to_seed(mnemonic, passphrase)
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed[:32])
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                methods.append((f"passphrase_{passphrase or 'empty'}", pubkey_hex))
            except:
                pass
        
        return methods
    
    def _alternative_methods(self, seed: bytes, mnemonic: str) -> List[Tuple[str, str]]:
        """Alternative derivation methods."""
        methods = []
        
        try:
            # Word concatenation
            words = mnemonic.split()
            word_entropy = "".join(words).encode()
            derived_seed = hashlib.sha256(word_entropy).digest()[:32]
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_seed)
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            methods.append(("word_concatenation", pubkey_hex))
            
            # BIP39 entropy direct
            entropy_hash = hashlib.sha256(" ".join(words).encode()).digest()[:32]
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(entropy_hash)
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            methods.append(("bip39_entropy_direct", pubkey_hex))
            
        except:
            pass
        
        return methods
    
    def _ledger_derivations(self, seed: bytes) -> List[Tuple[str, str]]:
        """Ledger-specific derivation methods."""
        methods = []
        
        # Ledger paths
        ledger_paths = [
            [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000],
            [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000, 0 + 0x80000000],
            [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000],
        ]
        
        for i, path in enumerate(ledger_paths):
            try:
                derived_key = self._ledger_bip32_ed25519(seed, path)
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                methods.append((f"ledger_hedera_{i+1}", pubkey_hex))
            except:
                pass
        
        return methods
    
    def _hashpack_derivations(self, seed: bytes) -> List[Tuple[str, str]]:
        """HashPack-specific derivation methods."""
        methods = []
        
        # HashPack custom paths (exact match from working code)
        hashpack_paths = [
            [44 + 0x80000000, 3030 + 0x80000000, 0 + 0x80000000, 0, 0],  # Non-hardened change/address
            [44 + 0x80000000, 3030 + 0x80000000, 0, 0],  # Shorter path ← This was the successful one!
            [44 + 0x80000000, 3030 + 0x80000000],  # Minimal HashPack path
            [44 + 0x80000000, 3030],  # Non-hardened coin type
        ]
        
        for i, path in enumerate(hashpack_paths):
            try:
                derived_key = self._bip32_ed25519_derive(seed, path)
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_key)
                public_key = private_key.public_key()
                pubkey_hex = public_key.public_bytes_raw().hex()
                methods.append((f"hashpack_path_{i+1}", pubkey_hex))
            except:
                pass
        
        return methods
    
    def _advanced_methods(self, seed: bytes, mnemonic: str) -> List[Tuple[str, str]]:
        """Advanced derivation methods."""
        methods = []
        
        try:
            # Web3 style
            web3_seed = hashlib.sha3_256(seed).digest()
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(web3_seed[:32])
            public_key = private_key.public_key()
            pubkey_hex = public_key.public_bytes_raw().hex()
            methods.append(("web3_style", pubkey_hex))
        except:
            pass
        
        return methods
    
    def _bip32_ed25519_derive(self, seed: bytes, path: List[int]) -> bytes:
        """Proper BIP32-Ed25519 derivation - Ed25519 uses hardened derivation only"""
        # Start with master key
        master_secret = hmac.new(b"ed25519 seed", seed, hashlib.sha512).digest()
        key = master_secret[:32]
        chain_code = master_secret[32:]
        
        for index in path:
            # Ed25519 uses hardened derivation only
            if index < 0x80000000:
                index += 0x80000000
            
            data = b'\x00' + key + index.to_bytes(4, 'big')
            mac = hmac.new(chain_code, data, hashlib.sha512).digest()
            key = mac[:32]
            chain_code = mac[32:]
        
        return key
    
    def _ledger_bip32_ed25519(self, seed: bytes, path: List[int]) -> bytes:
        """Ledger-specific BIP32 Ed25519 derivation."""
        master_secret = hmac.new(b"Ledger seed", seed, hashlib.sha512).digest()
        key = master_secret[:32]
        chain_code = master_secret[32:]
        
        for index in path:
            if index < 0x80000000:
                index += 0x80000000
            
            data = b'\x00' + key + index.to_bytes(4, 'big')
            mac = hmac.new(chain_code, data, hashlib.sha512).digest()
            key = mac[:32]
            chain_code = mac[32:]
        
        return key
    
    def _metamask_derivation(self, seed: bytes) -> str:
        """MetaMask-style derivation."""
        try:
            # MetaMask uses different derivation
            derived_seed = hashlib.sha256(seed + b"metamask").digest()[:32]
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_seed)
            public_key = private_key.public_key()
            return public_key.public_bytes_raw().hex()
        except:
            return ""
    
    def _hashpack_derivation(self, seed: bytes) -> str:
        """HashPack-style derivation."""
        try:
            derived_seed = hashlib.sha256(seed + b"hashpack").digest()[:32]
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_seed)
            public_key = private_key.public_key()
            return public_key.public_bytes_raw().hex()
        except:
            return ""
    
    def _blade_derivation(self, seed: bytes) -> str:
        """Blade wallet derivation."""
        try:
            derived_seed = hashlib.sha256(seed + b"blade").digest()[:32]
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_seed)
            public_key = private_key.public_key()
            return public_key.public_bytes_raw().hex()
        except:
            return ""
    
    def _secp256k1_derivation(self, seed: bytes) -> str:
        """Secp256k1-style derivation (converted to Ed25519)."""
        try:
            derived_seed = hashlib.sha256(seed + b"secp256k1").digest()[:32]
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived_seed)
            public_key = private_key.public_key()
            return public_key.public_bytes_raw().hex()
        except:
            return ""
