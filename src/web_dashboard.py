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
import re
from datetime import datetime, timedelta
from collections import defaultdict, deque
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

class DataAnalyzer:
    """Analizator danych w czasie rzeczywistym dla dashboard"""
    
    def __init__(self):
        self.order_history = deque(maxlen=1000)  # Ostatnie 1000 zamówień
        self.product_stats = defaultdict(lambda: {
            'count': 0, 'revenue': 0.0, 'category': '', 'name': ''
        })
        self.category_stats = defaultdict(lambda: {'count': 0, 'revenue': 0.0})
        self.hourly_stats = defaultdict(lambda: {'orders': 0, 'revenue': 0.0})
        self.recent_metrics = deque(maxlen=60)  # Ostatnie 60 pomiarów (5 min przy update co 5s)
        
    def parse_order_from_log(self, log_line):
        """Parsuje zamówienie z linii loga"""
        try:
            # Przykład: 2024-01-15 14:30:25 - order_simulator - INFO - Wysłano zamówienie: {...}
            if 'Wysłano zamówienie:' in log_line:
                json_start = log_line.find('{')
                if json_start != -1:
                    json_str = log_line[json_start:]
                    order_data = json.loads(json_str)
                    return order_data
        except Exception as e:
            pass
        return None
    
    def parse_analysis_from_log(self, log_line):
        """Parsuje wyniki analizy z loga data_analyzer"""
        try:
            # Parsowanie top produktów z logów
            if 'TOP PRODUKTY' in log_line and 'Batch' in log_line:
                batch_match = re.search(r'Batch (\d+)', log_line)
                return {'type': 'batch_start', 'batch_id': int(batch_match.group(1)) if batch_match else 0}
            
            # Parsowanie konkretnych produktów - lepszy regex
            # Przykład: " 1. Electronics Smart Watch 15    Sprzedane: 45    Przychód: $2,847.55"
            product_match = re.search(r'(\d+)\.\s+(.+?)\s+Sprzedane:\s*(\d+)', log_line)
            if product_match:
                rank = int(product_match.group(1))
                product_name = product_match.group(2).strip()
                count = int(product_match.group(3))
                
                # Szukaj przychodu w tej samej linii
                revenue_match = re.search(r'Przychód:\s*\$?([\d,]+\.?\d*)', log_line)
                revenue = float(revenue_match.group(1).replace(',', '')) if revenue_match else 0.0
                
                return {
                    'type': 'product_rank',
                    'rank': rank,
                    'product_name': product_name,
                    'count': count,
                    'revenue': revenue
                }
                
            # Parsowanie statystyk kategorii
            category_match = re.search(r'Kategoria:\s*(.+?)\s+Zamówienia:\s*(\d+)', log_line)
            if category_match:
                category = category_match.group(1).strip()
                count = int(category_match.group(2))
                return {
                    'type': 'category_stat',
                    'category': category,
                    'count': count
                }
        except Exception as e:
            pass
        return None
    
    def add_order(self, order_data):
        """Dodaje zamówienie do analizy"""
        if not order_data:
            return
            
        try:
            timestamp = datetime.now()
            order_data['parsed_timestamp'] = timestamp
            
            # Dodaj do historii
            self.order_history.append(order_data)
            
            # Aktualizuj statystyki produktów
            product_id = order_data.get('product_id', '')
            product_name = order_data.get('product_name', '')
            category = order_data.get('category', '')
            price = float(order_data.get('price', 0))
            quantity = int(order_data.get('quantity', 1))
            revenue = price * quantity
            
            self.product_stats[product_id]['count'] += quantity
            self.product_stats[product_id]['revenue'] += revenue
            self.product_stats[product_id]['category'] = category
            self.product_stats[product_id]['name'] = product_name
            
            # Aktualizuj statystyki kategorii
            self.category_stats[category]['count'] += quantity
            self.category_stats[category]['revenue'] += revenue
            
            # Aktualizuj statystyki godzinowe
            hour_key = timestamp.strftime('%H:%M')
            self.hourly_stats[hour_key]['orders'] += 1
            self.hourly_stats[hour_key]['revenue'] += revenue
            
        except Exception as e:
            logging.error(f"Błąd dodawania zamówienia: {e}")
    
    def get_top_products(self, limit=10):
        """Zwraca top produkty według liczby zamówień"""
        sorted_products = sorted(
            self.product_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        return [
            {
                'product_id': pid,
                'name': data['name'],
                'category': data['category'],
                'count': data['count'],
                'revenue': round(data['revenue'], 2)
            }
            for pid, data in sorted_products[:limit]
        ]
    
    def get_category_breakdown(self):
        """Zwraca breakdown według kategorii"""
        return [
            {
                'category': category,
                'count': data['count'],
                'revenue': round(data['revenue'], 2)
            }
            for category, data in self.category_stats.items()
        ]
    
    def get_hourly_trends(self, hours=24):
        """Zwraca trendy godzinowe"""
        now = datetime.now()
        hourly_data = []
        
        for i in range(hours):
            hour_time = now - timedelta(hours=i)
            hour_key = hour_time.strftime('%H:%M')
            stats = self.hourly_stats.get(hour_key, {'orders': 0, 'revenue': 0.0})
            
            hourly_data.append({
                'time': hour_key,
                'orders': stats['orders'],
                'revenue': round(stats['revenue'], 2)
            })
        
        return list(reversed(hourly_data))
    
    def get_real_time_metrics(self):
        """Zwraca metryki czasu rzeczywistego"""
        now = datetime.now()
        
        # Zamówienia z ostatniej minuty
        recent_orders = [
            order for order in self.order_history
            if 'parsed_timestamp' in order and 
            (now - order['parsed_timestamp']).total_seconds() < 60
        ]
        
        # Metryki
        orders_per_minute = len(recent_orders)
        revenue_per_minute = sum(
            float(order.get('price', 0)) * int(order.get('quantity', 1))
            for order in recent_orders
        )
        
        # Średnia wartość zamówienia
        avg_order_value = (
            revenue_per_minute / orders_per_minute 
            if orders_per_minute > 0 else 0
        )
        
        metrics = {
            'timestamp': now.strftime('%H:%M:%S'),
            'orders_per_minute': orders_per_minute,
            'revenue_per_minute': round(revenue_per_minute, 2),
            'avg_order_value': round(avg_order_value, 2),
            'total_orders': len(self.order_history),
            'total_products': len(self.product_stats),
            'total_categories': len(self.category_stats)
        }
        
        # Dodaj do historii metryk
        self.recent_metrics.append(metrics)
        
        return metrics

class SystemMonitor:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logs_dir = os.path.join(self.project_root, 'logs')
        self.pids_dir = os.path.join(self.project_root, 'pids')
        self.config_file = os.path.join(self.project_root, '.env')
        self.running = True
        
        # Analizator danych
        self.data_analyzer = DataAnalyzer()
        self.last_log_positions = {}  # Pozycje w plikach logów
        
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
    
    def parse_new_log_entries(self):
        """Parsuje nowe wpisy w logach do analizy danych"""
        try:
            # Parsuj logi order_simulator dla nowych zamówień
            self._parse_service_logs('order_simulator', self.data_analyzer.parse_order_from_log)
            
            # Parsuj logi data_analyzer dla wyników analiz
            self._parse_service_logs('data_analyzer', self.data_analyzer.parse_analysis_from_log)
            
        except Exception as e:
            logger.error(f"Błąd parsowania logów: {e}")
    
    def _parse_service_logs(self, service_name, parser_func):
        """Parsuje logi konkretnego serwisu"""
        log_file = os.path.join(self.logs_dir, f'{service_name}.log')
        
        if not os.path.exists(log_file):
            return
        
        try:
            # Sprawdź pozycję w pliku i modyfikację
            current_position = self.last_log_positions.get(service_name, 0)
            file_size = os.path.getsize(log_file)
            
            # Jeśli plik się zmniejszył (został wyczyszczony), zresetuj pozycję
            if file_size < current_position:
                current_position = 0
            
            with open(log_file, 'r') as f:
                f.seek(current_position)
                new_lines = f.readlines()
                
                # Parsuj nowe linie
                for line in new_lines:
                    parsed_data = parser_func(line.strip())
                    if parsed_data and service_name == 'order_simulator':
                        self.data_analyzer.add_order(parsed_data)
                
                # Aktualizuj pozycję
                self.last_log_positions[service_name] = f.tell()
                
        except Exception as e:
            logger.error(f"Błąd parsowania logów {service_name}: {e}")
            # Resetuj pozycję w przypadku błędu
            self.last_log_positions[service_name] = 0
    
    def get_analytics_data(self):
        """Zwraca dane analityczne do dashboard"""
        return {
            'real_time_metrics': self.data_analyzer.get_real_time_metrics(),
            'top_products': self.data_analyzer.get_top_products(10),
            'category_breakdown': self.data_analyzer.get_category_breakdown(),
            'hourly_trends': self.data_analyzer.get_hourly_trends(12),
            'recent_metrics_history': list(self.data_analyzer.recent_metrics)
        }
    
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

@app.route('/api/analytics')
def api_analytics():
    """API endpoint dla danych analitycznych"""
    return jsonify(monitor.get_analytics_data())

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
            # Parsuj nowe wpisy w logach
            monitor.parse_new_log_entries()
            
            # Wyślij status systemu
            status = monitor.get_system_status()
            socketio.emit('status_update', status)
            
            # Wyślij dane analityczne
            analytics = monitor.get_analytics_data()
            socketio.emit('analytics_update', analytics)
            
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
