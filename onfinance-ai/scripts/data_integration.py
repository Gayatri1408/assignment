# scripts/data_integration.py
import requests
import sqlite3
import logging
import time
import os
import sys

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/data_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SafeAPiFetcher:
    def __init__(self, primary_url="https://api.publicapis.org/entries", fallback_url=None):
        self.primary_url = primary_url
        self.fallback_url = fallback_url
        self.session = requests.Session()
        self.session.mount('https://', requests.adapters.HTTPAdapter(
            max_retries=5,
            pool_connections=10,
            pool_maxsize=100
        ))
    
    def fetch(self):
        try:
            # Primary request
            response = self.session.get(
                self.primary_url,
                headers={"User-Agent": "OnFinanceAI/1.0"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.warning(f"Primary API fetch failed: {str(e)}")
            
            # If no fallback URL, re-raise the exception
            if not self.fallback_url:
                raise
            
            # Try fallback
            try:
                response = self.session.get(
                    self.fallback_url,
                    headers={"User-Agent": "OnFinanceAI/1.0"},
                    timeout=15
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as fallback_error:
                logging.error(f"Fallback API fetch failed: {str(fallback_error)}")
                raise

def update_database():
    try:
        fetcher = SafeAPiFetcher()
        data = fetcher.fetch()
        
        # Extract entries, limiting to 10 for testing
        entries = data.get('entries', [])[:10]
        
        with sqlite3.connect('data/onfinance.db') as conn:
            for entry in entries:
                conn.execute('''
                    INSERT OR REPLACE INTO apis (name, description, category)
                    VALUES (?, ?, ?)
                ''', (
                    entry.get('API', 'Unknown'),
                    entry.get('Description', ''),
                    entry.get('Category', 'General')
                ))
            
            conn.commit()
            logging.info(f"Successfully updated {len(entries)} API records")
    except Exception as e:
        logging.error(f"Data pipeline failure: {str(e)}")

def run_pipeline():
    logging.info("Data integration pipeline started")
    while True:
        try:
            update_database()
        except Exception as e:
            logging.error(f"Pipeline iteration failed: {str(e)}")
        
        # Sleep for 5 minutes between updates
        time.sleep(300)

if __name__ == '__main__':
    try:
        run_pipeline()
    except KeyboardInterrupt:
        logging.info("Data pipeline stopped by user")
        sys.exit(0)
