#!/usr/bin/env python3
"""
Web Dashboard dla Online Store Order Analysis
Interfejs webowy do monitorowania i konfiguracji systemu
"""

import os
import json
import time
import signal
import subprocess
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import logging
import psutil
import configparser

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aseed-dashboard-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

class SystemMonitor:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logs_dir = os.path.join(self.project_root, 'logs')
        self.pids_dir = os.path.join(self.project_root, 'pids')
        self.config_file = os.path.join(self.project_root, '.env')
        self.running = True
        
        # Sprawdź czy katalogi istnieją
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.pids_dir, exist_ok=True)
    
    def get_system_status(self):
        """Pobiera status wszystkich komponentów systemu"""
        status = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'zookeeper': self._check_process_status('zookeeper'),
            'kafka': self._check_process_status('kafka'),
            'order_simulator': self._check_process_status('order_simulator'),
            'data_analyzer': self._check_process_status('data_analyzer'),
            'system_resources': self._get_system_resources()
        }
        return status
    
    def _check_process_status(self, service_name):
        """Sprawdza status procesu na podstawie PID file"""
        pid_file = os.path.join(self.pids_dir, f'{service_name}.pid')
        
        if not os.path.exists(pid_file):
            return {'status': 'stopped', 'pid': None, 'uptime': None}
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                uptime = time.time() - process.create_time()
                return {
                    'status': 'running',
                    'pid': pid,
                    'uptime': self._format_uptime(uptime),
                    'cpu_percent': process.cpu_percent(),
                    'memory_mb': process.memory_info().rss / 1024 / 1024
                }
            else:
                # PID file istnieje, ale proces nie
                os.remove(pid_file)
                return {'status': 'stopped', 'pid': None, 'uptime': None}
                
        except Exception as e:
            logger.error(f"Błąd sprawdzania statusu {service_name}: {e}")
            return {'status': 'error', 'pid': None, 'uptime': None, 'error': str(e)}
    
    def _get_system_resources(self):
        """Pobiera informacje o zasobach systemowych"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }
    
    def _format_uptime(self, seconds):
        """Formatuje uptime w czytelny sposób"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def get_recent_logs(self, service_name, lines=50):
        """Pobiera ostatnie logi dla danego serwisu"""
        log_file = os.path.join(self.logs_dir, f'{service_name}.log')
        
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return [line.strip() for line in all_lines[-lines:]]
        except Exception as e:
            logger.error(f"Błąd odczytu logów {service_name}: {e}")
            return [f"Błąd odczytu logów: {e}"]
    
    def get_configuration(self):
        """Pobiera aktualną konfigurację z pliku .env"""
        config = {}
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            except Exception as e:
                logger.error(f"Błąd odczytu konfiguracji: {e}")
        
        # Domyślne wartości jeśli nie ma pliku .env
        default_config = {
            'KAFKA_BOOTSTRAP_SERVERS': 'localhost:9092',
            'KAFKA_TOPIC': 'orders',
            'ORDERS_PER_SECOND': '2',
            'PRODUCT_COUNT': '50',
            'SPARK_MASTER_URL': 'local[*]'
        }
        
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        
        return config
    
    def update_configuration(self, new_config):
        """Aktualizuje konfigurację w pliku .env"""
        try:
            with open(self.config_file, 'w') as f:
                f.write("# Konfiguracja ASEED - Online Store Order Analysis\n")
                f.write("# Zmieniono przez Web Dashboard\n\n")
                
                f.write("# Konfiguracja Kafka\n")
                f.write(f"KAFKA_BOOTSTRAP_SERVERS={new_config.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')}\n")
                f.write(f"KAFKA_TOPIC={new_config.get('KAFKA_TOPIC', 'orders')}\n\n")
                
                f.write("# Konfiguracja symulatora\n")
                f.write(f"ORDERS_PER_SECOND={new_config.get('ORDERS_PER_SECOND', '2')}\n")
                f.write(f"PRODUCT_COUNT={new_config.get('PRODUCT_COUNT', '50')}\n\n")
                
                f.write("# Konfiguracja Spark\n")
                f.write(f"SPARK_MASTER_URL={new_config.get('SPARK_MASTER_URL', 'local[*]')}\n")
            
            return True
        except Exception as e:
            logger.error(f"Błąd zapisu konfiguracji: {e}")
            return False
    
    def execute_command(self, command):
        """Wykonuje komendę systemową"""
        try:
            os.chdir(self.project_root)
            
            if command == 'start':
                result = subprocess.run(['./start.sh'], capture_output=True, text=True, timeout=60)
            elif command == 'stop':
                result = subprocess.run(['./stop.sh'], capture_output=True, text=True, timeout=30)
            elif command == 'install':
                result = subprocess.run(['./install.sh'], capture_output=True, text=True, timeout=600)
            elif command == 'check':
                result = subprocess.run(['./check-requirements.sh'], capture_output=True, text=True, timeout=30)
            else:
                return {'success': False, 'message': f'Nieznana komenda: {command}'}
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Timeout - komenda trwała zbyt długo'}
        except Exception as e:
            return {'success': False, 'message': f'Błąd wykonania: {str(e)}'}

# Globalny monitor systemu
monitor = SystemMonitor()

@app.route('/')
def dashboard():
    """Główny dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint dla statusu systemu"""
    return jsonify(monitor.get_system_status())

@app.route('/api/logs/<service_name>')
def api_logs(service_name):
    """API endpoint dla logów"""
    lines = request.args.get('lines', 50, type=int)
    logs = monitor.get_recent_logs(service_name, lines)
    return jsonify({'logs': logs})

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API endpoint dla konfiguracji"""
    if request.method == 'GET':
        return jsonify(monitor.get_configuration())
    
    elif request.method == 'POST':
        new_config = request.json
        success = monitor.update_configuration(new_config)
        return jsonify({'success': success})

@app.route('/api/command/<command>', methods=['POST'])
def api_command(command):
    """API endpoint dla wykonywania komend"""
    result = monitor.execute_command(command)
    return jsonify(result)

@socketio.on('connect')
def handle_connect():
    """Obsługa połączenia WebSocket"""
    logger.info('Klient połączony z WebSocket')
    emit('status', monitor.get_system_status())

@socketio.on('request_status')
def handle_status_request():
    """Obsługa żądania statusu przez WebSocket"""
    emit('status', monitor.get_system_status())

def background_status_updater():
    """Wątek w tle wysyłający aktualizacje statusu"""
    while monitor.running:
        try:
            status = monitor.get_system_status()
            socketio.emit('status_update', status)
            time.sleep(5)  # Aktualizuj co 5 sekund
        except Exception as e:
            logger.error(f"Błąd w background updater: {e}")
            time.sleep(10)

def signal_handler(signum, frame):
    """Obsługa sygnałów"""
    logger.info("Otrzymano sygnał zamknięcia")
    monitor.running = False

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Uruchom wątek w tle do aktualizacji statusu
    status_thread = threading.Thread(target=background_status_updater, daemon=True)
    status_thread.start()
    
    logger.info("Uruchamianie Web Dashboard na http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
