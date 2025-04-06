from flask import Flask, jsonify, request
import sqlite3

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
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Replace service registration code

