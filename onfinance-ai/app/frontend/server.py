# app/backend/app.py
from flask import Flask, jsonify, request
import sqlite3
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    filename='logs/backend.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

def create_app():
    app = Flask(__name__)
    
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "version": "1.0.0"})
    
    @app.route('/data')
    def get_data():
        try:
            with sqlite3.connect('data/onfinance.db') as conn:
                cursor = conn.execute("SELECT * FROM apis")
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return jsonify(results)
        except Exception as e:
            logging.error(f"Database error: {str(e)}")
            return jsonify({"error": "Service unavailable"}), 503
    
    @app.route('/api/data', methods=['GET'])
    def api_data():
        return get_data()
    
    @app.after_request
    def after_request(response):
        logging.info(f"{request.method} {request.path} {response.status_code}")
        return response
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
