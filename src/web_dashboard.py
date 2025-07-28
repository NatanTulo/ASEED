#!/usr/bin/env python3
"""
Simplified Real-time Dashboard for Spark Streaming Analytics
Receives data directly from Spark Structured Streaming
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
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
        
        # Start background thread to calculate metrics
        self._start_metrics_thread()
        
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

# Global dashboard instance
dashboard = RealTimeDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'total_orders': dashboard.total_orders,
        'total_revenue': dashboard.total_revenue,
        'orders_per_minute': dashboard.orders_per_minute
    })

@app.route('/api/top_products', methods=['POST'])
def receive_top_products():
    """Receive top products data from Spark"""
    try:
        data = request.json
        dashboard.latest_top_products = data['products']
        
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
        dashboard.latest_categories = data['categories']
        
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
        orders = data['orders']
        
        # Add to recent orders (limit to last 20 to prevent memory issues)
        current_time = datetime.now()
        for order in orders:
            dashboard.latest_raw_orders.append(order)
            # Store timestamp for orders/minute calculation
            dashboard.order_timestamps.append(current_time)
        
        # Keep only last 20 orders in memory
        while len(dashboard.latest_raw_orders) > 20:
            dashboard.latest_raw_orders.popleft()
        
        # Update counters
        dashboard.total_orders += len(orders)
        dashboard.total_revenue += sum(order['total_value'] for order in orders)
        
        # Update orders/minute immediately for faster response
        dashboard._update_orders_per_minute()
        
        logger.info(f"Received {len(orders)} raw orders from Spark")
        
        # Emit to connected clients - send only last 10
        socketio.emit('raw_orders_update', {
            'orders': list(dashboard.latest_raw_orders),  # All stored orders
            'total_orders': dashboard.total_orders,
            'total_revenue': dashboard.total_revenue,
            'orders_per_minute': dashboard.orders_per_minute
        })
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error receiving raw orders: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dashboard_data')
def get_dashboard_data():
    """Get all current dashboard data"""
    return jsonify({
        'top_products': dashboard.latest_top_products,
        'categories': dashboard.latest_categories,
        'recent_orders': list(dashboard.latest_raw_orders),  # All stored orders (max 20)
        'metrics': {
            'total_orders': dashboard.total_orders,
            'total_revenue': dashboard.total_revenue,
            'orders_per_minute': dashboard.orders_per_minute
        },
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected to dashboard')
    
    # Send current data to newly connected client
    emit('initial_data', {
        'top_products': dashboard.latest_top_products,
        'categories': dashboard.latest_categories,
        'recent_orders': list(dashboard.latest_raw_orders),  # All stored orders
        'metrics': {
            'total_orders': dashboard.total_orders,
            'total_revenue': dashboard.total_revenue,
            'orders_per_minute': dashboard.orders_per_minute
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
    logger.info("Starting Real-time Spark Dashboard on http://localhost:5005")
    socketio.run(app, host='0.0.0.0', port=5005, debug=False)
