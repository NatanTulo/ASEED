#!/usr/bin/env python3
"""
Simplified Real-time Dashboard for Spark Streaming Analytics
Receives data directly from Spark Structured Streaming
"""

import os
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict, deque
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging

# Konfiguracja logowania
log_file = '/app/logs/dashboard.log' if os.path.exists('/app/logs') else 'dashboard.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aseed-dashboard-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

class RealTimeDashboard:
    """Real-time dashboard receiving data from Spark"""
    
    def __init__(self):
        # Store latest data from Spark
        self.latest_top_products = []
        self.latest_categories = []
        self.latest_raw_orders = deque(maxlen=20)  # Keep last 20 orders only
        
        # Metrics over time for orders/minute calculation
        self.order_timestamps = deque(maxlen=1000)  # Store timestamps of last 1000 orders
        
        # Real-time counters
        self.total_orders = 0
        self.total_revenue = 0.0
        self.orders_per_minute = 0
        
        # Service status tracking
        self.service_status = {
            'zookeeper': {'status': 'unknown', 'pid': None, 'last_check': None},
            'kafka': {'status': 'unknown', 'pid': None, 'last_check': None},
            'order_simulator': {'status': 'unknown', 'pid': None, 'last_check': None},
            'data_analyzer': {'status': 'unknown', 'pid': None, 'last_check': None},
            'dashboard': {'status': 'running', 'pid': os.getpid(), 'last_check': datetime.now()}
        }
        
        # Start background thread to calculate metrics
        self._start_metrics_thread()
        
        # Start background thread to monitor services
        self._start_service_monitor()
        
        logger.info("Dashboard initialized and ready to receive Spark data")
    
    def _start_metrics_thread(self):
        """Start background thread to calculate orders/minute"""
        def calculate_metrics():
            while True:
                time.sleep(10)  # Update every 10 seconds
                self._update_orders_per_minute()
        
        thread = threading.Thread(target=calculate_metrics, daemon=True)
        thread.start()
    
    def _update_orders_per_minute(self):
        """Calculate orders per minute based on recent timestamps"""
        if len(self.order_timestamps) < 2:
            self.orders_per_minute = 0
            return
        
        # Get current time and 1 minute ago
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Count orders in the last minute
        recent_orders = [ts for ts in self.order_timestamps if ts >= one_minute_ago]
        self.orders_per_minute = len(recent_orders)
        
        logger.debug(f"Calculated {self.orders_per_minute} orders/minute")
    
    def _start_service_monitor(self):
        """Start background thread to monitor service status"""
        def monitor_services():
            while True:
                try:
                    self._check_service_status()
                    
                    # Convert datetime objects to strings for JSON serialization
                    services_for_emit = {}
                    for service, status in self.service_status.items():
                        services_for_emit[service] = {**status}
                        if 'last_check' in services_for_emit[service] and services_for_emit[service]['last_check']:
                            services_for_emit[service]['last_check'] = services_for_emit[service]['last_check'].isoformat()
                    
                    # Emit status update to connected clients
                    socketio.emit('service_status_update', {
                        'services': services_for_emit,
                        'timestamp': datetime.now().isoformat()
                    })
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    logger.error(f"Error monitoring services: {e}")
                    time.sleep(10)  # Longer sleep on error
        
        thread = threading.Thread(target=monitor_services, daemon=True)
        thread.start()
        logger.info("Monitoring serwisów uruchomiony")
    
    def _check_service_status(self):
        """Check status of all ASEED Docker containers"""
        try:
            # Get Docker container statuses
            result = subprocess.run(['docker', 'ps', '--filter', 'name=aseed-', '--format', 'table {{.Names}}\t{{.Status}}\t{{.ID}}'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.error(f"Docker ps command failed: {result.stderr}")
                # Set all services to error state
                for service in self.service_status:
                    if service != 'dashboard':
                        self.service_status[service] = {
                            'status': 'error',
                            'pid': None,
                            'last_check': datetime.now(),
                            'error': 'Docker not available'
                        }
                return
            
            # Parse container info
            container_info = {}
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if line.strip():
                    # Split by whitespace and extract name, status, and container ID
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]  # First part is container name
                        # Status is everything except first and last part
                        status = ' '.join(parts[1:-1])  # Middle parts are status
                        container_id = parts[-1]  # Last part is container ID
                        
                        # Map container names to service names
                        service_name = None
                        if 'zookeeper' in name:
                            service_name = 'zookeeper'
                        elif 'kafka' in name:
                            service_name = 'kafka'
                        elif 'order-simulator' in name:
                            service_name = 'order_simulator'
                        elif 'data-analyzer' in name:
                            service_name = 'data_analyzer'
                        elif 'web-dashboard' in name:
                            continue  # Skip dashboard - we handle it separately
                        
                        if service_name:
                            # Determine status from Docker status
                            if 'Up' in status and 'healthy' in status:
                                container_status = 'running'
                            elif 'Up' in status:
                                container_status = 'running'
                            elif 'Exited' in status:
                                container_status = 'stopped'
                            else:
                                container_status = 'unknown'
                            
                            container_info[service_name] = {
                                'status': container_status,
                                'pid': container_id,  # Use container ID as PID equivalent
                                'last_check': datetime.now(),
                                'docker_status': status
                            }
            
            # Update service status for all known services
            for service in ['zookeeper', 'kafka', 'order_simulator', 'data_analyzer']:
                if service in container_info:
                    self.service_status[service] = container_info[service]
                else:
                    # Container not running or not found
                    self.service_status[service] = {
                        'status': 'not_started',
                        'pid': None,
                        'last_check': datetime.now()
                    }
            
        except subprocess.TimeoutExpired:
            logger.error("Docker ps command timed out")
            for service in self.service_status:
                if service != 'dashboard':
                    self.service_status[service] = {
                        'status': 'error',
                        'pid': None,
                        'last_check': datetime.now(),
                        'error': 'Docker command timeout'
                    }
        except Exception as e:
            logger.error(f"Error checking Docker container status: {e}")
            for service in self.service_status:
                if service != 'dashboard':
                    self.service_status[service] = {
                        'status': 'error',
                        'pid': None,
                        'last_check': datetime.now(),
                        'error': str(e)
                    }

# Global dashboard instance
dashboard = None

def get_dashboard():
    """Get dashboard instance, create if needed"""
    global dashboard
    if dashboard is None:
        dashboard = RealTimeDashboard()
    return dashboard

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    dash = get_dashboard()
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'total_orders': dash.total_orders,
        'total_revenue': dash.total_revenue,
        'orders_per_minute': dash.orders_per_minute
    })

@app.route('/api/services')
def api_services():
    """API endpoint for service status"""
    dash = get_dashboard()
    return jsonify({
        'services': dash.service_status,
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'healthy' if all(
            s['status'] == 'running' for s in dash.service_status.values()
        ) else 'degraded'
    })

@app.route('/api/service-status')
def get_service_status():
    """API endpoint zwracający status wszystkich serwisów"""
    dash = get_dashboard()
    dash._check_service_status()  # Aktualizuj status przed zwróceniem
    
    # Konwertuj datetime na string dla JSON
    services_for_api = {}
    for service, status in dash.service_status.items():
        services_for_api[service] = {**status}
        if 'last_check' in services_for_api[service] and services_for_api[service]['last_check']:
            services_for_api[service]['last_check'] = services_for_api[service]['last_check'].isoformat()
    
    # Oblicz ogólny status systemu
    all_services = ['zookeeper', 'kafka', 'order_simulator', 'data_analyzer', 'dashboard']
    running_count = sum(1 for service in all_services if dash.service_status[service]['status'] == 'running')
    
    overall_status = 'healthy' if running_count == len(all_services) else \
                    'partial' if running_count > 0 else 'down'
    
    return jsonify({
        'overall_status': overall_status,
        'services': services_for_api,
        'summary': {
            'total_services': len(all_services),
            'running': running_count,
            'stopped': len(all_services) - running_count
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/top_products', methods=['POST'])
def receive_top_products():
    """Receive top products data from Spark"""
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
            
        dash = get_dashboard()
        dash.latest_top_products = data['products']
        
        logger.info(f"Received {len(data['products'])} top products from Spark")
        
        # Emit to connected clients
        socketio.emit('top_products_update', data)
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error receiving top products: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/categories', methods=['POST'])
def receive_categories():
    """Receive categories data from Spark"""
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
            
        dash = get_dashboard()
        dash.latest_categories = data['categories']
        
        logger.info(f"Received {len(data['categories'])} categories from Spark")
        
        # Emit to connected clients
        socketio.emit('categories_update', data)
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error receiving categories: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/raw_orders', methods=['POST'])
def receive_raw_orders():
    """Receive raw orders data from Spark"""
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
            
        orders = data['orders']
        dash = get_dashboard()
        
        # Add to recent orders (limit to last 20 to prevent memory issues)
        current_time = datetime.now()
        for order in orders:
            dash.latest_raw_orders.append(order)
            # Store timestamp for orders/minute calculation
            dash.order_timestamps.append(current_time)
        
        # Keep only last 20 orders in memory
        while len(dash.latest_raw_orders) > 20:
            dash.latest_raw_orders.popleft()
        
        # Update counters
        dash.total_orders += len(orders)
        dash.total_revenue += sum(order['total_value'] for order in orders)
        
        # Update orders/minute immediately for faster response
        dash._update_orders_per_minute()
        
        logger.info(f"Received {len(orders)} raw orders from Spark")
        
        # Emit to connected clients - send only last 10
        socketio.emit('raw_orders_update', {
            'orders': list(dash.latest_raw_orders),  # All stored orders
            'total_orders': dash.total_orders,
            'total_revenue': dash.total_revenue,
            'orders_per_minute': dash.orders_per_minute
        })
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error receiving raw orders: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dashboard_data')
def get_dashboard_data():
    """Get all current dashboard data"""
    dash = get_dashboard()
    return jsonify({
        'top_products': dash.latest_top_products,
        'categories': dash.latest_categories,
        'recent_orders': list(dash.latest_raw_orders),  # All stored orders (max 20)
        'metrics': {
            'total_orders': dash.total_orders,
            'total_revenue': dash.total_revenue,
            'orders_per_minute': dash.orders_per_minute
        },
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected to dashboard')
    
    dash = get_dashboard()
    # Send current data to newly connected client
    emit('initial_data', {
        'top_products': dash.latest_top_products,
        'categories': dash.latest_categories,
        'recent_orders': list(dash.latest_raw_orders),  # All stored orders
        'metrics': {
            'total_orders': dash.total_orders,
            'total_revenue': dash.total_revenue,
            'orders_per_minute': dash.orders_per_minute
        }
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected from dashboard')

def calculate_metrics():
    """Calculate real-time metrics"""
    # This would run periodically to calculate orders per minute etc.
    # For now, we'll keep it simple
    pass

if __name__ == '__main__':
    logger.info("Starting ASEED Real-time Dashboard")
    
    # Get host and port from environment variables (for Docker)
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5005'))
    
    logger.info(f"Dashboard będzie dostępny na: http://{host}:{port}")
    
    # Initialize global dashboard instance
    dashboard = RealTimeDashboard()
    
    try:
        socketio.run(app, 
                    host=host, 
                    port=port, 
                    debug=False,
                    allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("Dashboard zatrzymany")
    except Exception as e:
        logger.error(f"Błąd dashboardu: {e}")
        raise
