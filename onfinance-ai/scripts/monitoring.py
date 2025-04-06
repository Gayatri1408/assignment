# scripts/monitoring.py
import psutil
import time
import logging
import os
import csv
import datetime
import sys

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/monitoring.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ensure metrics directory exists
os.makedirs('metrics', exist_ok=True)

def get_process_info(process_name):
    """Get information about a running process by name"""
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        if process_name in proc.info['name']:
            return {
                'pid': proc.info['pid'],
                'cpu_percent': proc.info['cpu_percent'],
                'memory_mb': proc.info['memory_info'].rss / (1024 * 1024),
                'status': 'running'
            }
    return {'pid': None, 'cpu_percent': 0, 'memory_mb': 0, 'status': 'stopped'}

def check_port(port):
    """Check if a port is in use"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True
    return False

def collect_metrics():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Collect system metrics
    system_metrics = {
        'timestamp': timestamp,
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
    }
    
    # Collect process metrics
    frontend_metrics = get_process_info('python')  # Better to filter by script name
    backend_metrics = get_process_info('python')   # Better to filter by script name
    pipeline_metrics = get_process_info('python')  # Better to filter by script name
    
    # Check service status by ports
    frontend_port_status = check_port(8000)
    backend_port_status = check_port(5000)
    
    # Combine all metrics
    metrics = {
        **system_metrics,
        'frontend_status': 'running' if frontend_port_status else 'stopped',
        'backend_status': 'running' if backend_port_status else 'stopped',
        'frontend_memory_mb': frontend_metrics['memory_mb'],
        'backend_memory_mb': backend_metrics['memory_mb'],
        'pipeline_memory_mb': pipeline_metrics['memory_mb'],
    }
    
    # Write to CSV
    filename = f"metrics/onfinance_metrics_{datetime.datetime.now().strftime('%Y-%m-%d')}.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(metrics)
    
    return metrics

def run_monitoring():
    logging.info("Monitoring service started")
    
    while True:
        try:
            metrics = collect_metrics()
            logging.info(f"Collected metrics: CPU: {metrics['cpu_percent']}%, MEM: {metrics['memory_percent']}%")
            
            # Check health and log warnings/errors
            if metrics['cpu_percent'] > 80:
                logging.warning(f"High CPU usage: {metrics['cpu_percent']}%")
            
            if metrics['memory_percent'] > 80:
                logging.warning(f"High memory usage: {metrics['memory_percent']}%")
            
            if metrics['frontend_status'] == 'stopped':
                logging.error("Frontend service is not running!")
            
            if metrics['backend_status'] == 'stopped':
                logging.error("Backend service is not running!")
            
        except Exception as e:
            logging.error(f"Monitoring error: {str(e)}")
        
        # Sleep for 1 minute
        time.sleep(60)

if __name__ == '__main__':
    try:
        run_monitoring()
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")
        sys.exit(0)
