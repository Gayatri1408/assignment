# watchdog.py
import subprocess
import time
import logging
import os
import sys
import psutil

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/watchdog.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SERVICES = [
    {"name": "frontend", "script": "app/frontend/server.py", "port": 8000},
    {"name": "backend", "script": "app/backend/app.py", "port": 5000},
    {"name": "data_pipeline", "script": "scripts/data_integration.py", "port": None},
    {"name": "monitoring", "script": "scripts/monitoring.py", "port": None}
]

def is_port_in_use(port):
    """Check if a port is in use"""
    if port is None:
        return False
        
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True
    return False

def is_script_running(script_name):
    """Check if a Python script is running"""
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and len(cmdline) > 1 and 'python' in cmdline[0] and script_name in cmdline[1]:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def start_service(service):
    """Start a service if it's not running"""
    try:
        # Check if already running by port or process
        if service["port"] and is_port_in_use(service["port"]):
            logging.info(f"Service {service['name']} already running on port {service['port']}")
            return
            
        if is_script_running(service["script"]):
            logging.info(f"Service {service['name']} already running")
            return
        
        # Start the service
        logging.info(f"Starting service: {service['name']}")
        subprocess.Popen(
            ["python", service["script"]], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        logging.info(f"Started service: {service['name']}")
    except Exception as e:
        logging.error(f"Failed to start {service['name']}: {str(e)}")

def run_watchdog():
    logging.info("Watchdog service started")
    
    while True:
        for service in SERVICES:
            try:
                # Check if service is running by port (if applicable)
                is_running_by_port = False
                if service["port"]:
                    is_running_by_port = is_port_in_use(service["port"])
                
                # Check if service is running by script name
                is_running_by_script = is_script_running(service["script"])
                
                # If not running by either check, start the service
                if not (is_running_by_port or is_running_by_script):
                    logging.warning(f"Service {service['name']} is not running, restarting...")
                    start_service(service)
            except Exception as e:
                logging.error(f"Error checking {service['name']}: {str(e)}")
        
        # Sleep for 30 seconds
        time.sleep(30)

if __name__ == '__main__':
    try:
        run_watchdog()
    except KeyboardInterrupt:
        logging.info("Watchdog stopped by user")
        sys.exit(0)
