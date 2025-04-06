# scripts/init_db.py
import sqlite3
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def initialize_database():
    try:
        # Create database directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Connect to the database (this will create it if it doesn't exist)
        with sqlite3.connect('data/onfinance.db') as conn:
            # Enable Write-Ahead Logging for better performance
            conn.execute("PRAGMA journal_mode=WAL")
            
            # Create APIs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS apis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    description TEXT,
                    category TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create users table for future authentication
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    email TEXT UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert initial test data
            conn.execute('''
                INSERT OR IGNORE INTO apis (name, description, category)
                VALUES 
                    ("Test API 1", "Description for test API 1", "Finance"),
                    ("Test API 2", "Description for test API 2", "Data")
            ''')
            
            conn.commit()
            logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    initialize_database()
    logging.info("Database setup complete!")
