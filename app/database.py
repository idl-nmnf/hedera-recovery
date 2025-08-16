"""Database operations for tracking recovery progress."""

import psycopg2
import logging
from typing import Optional
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


class Database:
    """Database operations for recovery progress tracking."""
    
    def __init__(self):
        self.connection_params = {
            'host': DB_HOST,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'dbname': DB_NAME
        }
    
    def get_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.connection_params)
    
    def init_database(self):
        """Initialize database tables."""
        conn = self.get_connection()
        cur = conn.cursor()
        
        # Create table with original schema for backwards compatibility
        cur.execute('''
            CREATE TABLE IF NOT EXISTS combinations (
                id SERIAL PRIMARY KEY,
                mnemonic TEXT UNIQUE,
                checked BOOLEAN DEFAULT FALSE,
                balance NUMERIC DEFAULT 0
            )
        ''')
        
        # Create index for fast mnemonic lookups
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_combinations_mnemonic 
            ON combinations(mnemonic)
        ''')
        
        # Create index for stats queries
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_combinations_checked_balance 
            ON combinations(checked, balance) WHERE checked = TRUE
        ''')
        
        # Add new columns if they don't exist
        try:
            cur.execute('ALTER TABLE combinations ADD COLUMN IF NOT EXISTS method_used TEXT')
            cur.execute('ALTER TABLE combinations ADD COLUMN IF NOT EXISTS accounts TEXT[]')
            cur.execute('ALTER TABLE combinations ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        except Exception as e:
            # Ignore errors if columns already exist or can't be added
            logging.warning(f"Could not add new columns: {e}")
        
        conn.commit()
        cur.close()
        conn.close()
        logging.info("Database initialized successfully")
    
    def save_result(self, mnemonic: str, balance: int = 0, 
                   method_used: str = "", accounts: list = None):
        """Save a tested mnemonic result."""
        if accounts is None:
            accounts = []
            
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Check if extended columns exist
            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'combinations' AND column_name IN ('method_used', 'accounts')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
            
            if 'method_used' in existing_columns and 'accounts' in existing_columns:
                # Use full schema
                cur.execute('''
                    INSERT INTO combinations (mnemonic, checked, balance, method_used, accounts)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (mnemonic) DO UPDATE SET
                        checked = EXCLUDED.checked,
                        balance = EXCLUDED.balance,
                        method_used = EXCLUDED.method_used,
                        accounts = EXCLUDED.accounts
                ''', (mnemonic, True, balance, method_used, accounts))
            else:
                # Use basic schema for backwards compatibility
                cur.execute('''
                    INSERT INTO combinations (mnemonic, checked, balance)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (mnemonic) DO UPDATE SET
                        checked = EXCLUDED.checked,
                        balance = EXCLUDED.balance
                ''', (mnemonic, True, balance))
            
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error saving result to database: {e}")
    
    def is_already_tested(self, mnemonic: str) -> bool:
        """Check if a mnemonic has already been tested."""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            cur.execute('SELECT checked FROM combinations WHERE mnemonic = %s', (mnemonic,))
            result = cur.fetchone()
            
            cur.close()
            conn.close()
            
            return result is not None and result[0]
        except Exception as e:
            logging.error(f"Error checking if mnemonic tested: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get recovery statistics."""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
                SELECT 
                    COUNT(*) as total_tested,
                    COUNT(*) FILTER (WHERE balance > 0) as wallets_found,
                    COALESCE(SUM(balance), 0) as total_balance
                FROM combinations 
                WHERE checked = TRUE
            ''')
            
            result = cur.fetchone()
            cur.close()
            conn.close()
            
            return {
                'total_tested': result[0] if result else 0,
                'wallets_found': result[1] if result else 0,
                'total_balance': result[2] if result else 0
            }
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {'total_tested': 0, 'wallets_found': 0, 'total_balance': 0}
    
    def reset_database(self):
        """Reset database - remove all existing data for fresh start."""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Drop and recreate table for complete reset
            cur.execute('DROP TABLE IF EXISTS combinations CASCADE')
            
            # Recreate with optimized schema
            cur.execute('''
                CREATE TABLE combinations (
                    id SERIAL PRIMARY KEY,
                    mnemonic TEXT UNIQUE NOT NULL,
                    checked BOOLEAN DEFAULT FALSE,
                    balance BIGINT DEFAULT 0,
                    method_used TEXT,
                    accounts TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create optimized indexes
            cur.execute('CREATE INDEX idx_combinations_mnemonic ON combinations(mnemonic)')
            cur.execute('CREATE INDEX idx_combinations_checked ON combinations(checked) WHERE checked = TRUE')
            cur.execute('CREATE INDEX idx_combinations_balance ON combinations(balance) WHERE balance > 0')
            cur.execute('CREATE INDEX idx_combinations_method ON combinations(method_used) WHERE method_used IS NOT NULL')
            cur.execute('CREATE INDEX idx_combinations_created_at ON combinations(created_at)')
            
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info("✅ Database reset successfully - fresh start!")
            print("✅ Database reset successfully - fresh start!")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error resetting database: {e}")
            print(f"❌ Error resetting database: {e}")
            return False
