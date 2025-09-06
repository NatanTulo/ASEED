#!/usr/bin/env python3
"""
Generator danych testowych dla Web Dashboard
Generuje przykładowe zamówienia i zapisuje je do logów
"""

import json
import time
import random
from datetime import datetime
from faker import Faker
import os

fake = Faker()

# Produkty przykładowe
PRODUCTS = [
    {'id': 'PROD-001', 'name': 'Electronics Smart Watch 15', 'category': 'Electronics', 'price': 299.99},
    {'id': 'PROD-002', 'name': 'Clothing Fashion Jacket', 'category': 'Clothing', 'price': 89.99},
    {'id': 'PROD-003', 'name': 'Books Python Programming', 'category': 'Books', 'price': 45.99},
    {'id': 'PROD-004', 'name': 'Home Coffee Machine', 'category': 'Home', 'price': 199.99},
    {'id': 'PROD-005', 'name': 'Sports Running Shoes', 'category': 'Sports', 'price': 129.99},
    {'id': 'PROD-006', 'name': 'Beauty Face Cream', 'category': 'Beauty', 'price': 39.99},
    {'id': 'PROD-007', 'name': 'Electronics Wireless Headphones', 'category': 'Electronics', 'price': 159.99},
    {'id': 'PROD-008', 'name': 'Clothing Designer T-Shirt', 'category': 'Clothing', 'price': 29.99},
    {'id': 'PROD-009', 'name': 'Books Data Science Guide', 'category': 'Books', 'price': 59.99},
    {'id': 'PROD-010', 'name': 'Home Kitchen Blender', 'category': 'Home', 'price': 79.99},
]

def generate_test_order():
    """Generuje przykładowe zamówienie"""
    product = random.choice(PRODUCTS)
    quantity = random.randint(1, 5)
    
    order = {
        'order_id': f'ORD-{random.randint(100000, 999999)}',
        'product_id': product['id'],
        'product_name': product['name'],
        'category': product['category'],
        'price': product['price'],
        'quantity': quantity,
        'customer_id': f'CUST-{random.randint(1000, 9999)}',
        'timestamp': datetime.now().isoformat()
    }
    
    return order

def write_to_log(log_file, message):
    """Zapisuje wiadomość do pliku loga"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - order_simulator - INFO - Wysłano zamówienie: {json.dumps(message)}\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)

def generate_test_data(duration_minutes=5, orders_per_minute=10):
    """Generuje dane testowe przez określony czas"""
    print(f"Generowanie danych testowych przez {duration_minutes} minut...")
    print(f"Częstotliwość: {orders_per_minute} zamówień/minutę")
    
    # Upewnij się, że katalog logs istnieje (względem głównego katalogu)
    logs_dir = '../logs'
    os.makedirs(logs_dir, exist_ok=True)
    
    log_file = os.path.join(logs_dir, 'order_simulator.log')
    
    # Czyść istniejący log
    with open(log_file, 'w') as f:
        f.write("")
    
    total_orders = duration_minutes * orders_per_minute
    sleep_interval = 60.0 / orders_per_minute  # sekund między zamówieniami
    
    print(f"Rozpoczynam generowanie {total_orders} zamówień...")
    
    for i in range(total_orders):
        order = generate_test_order()
        write_to_log(log_file, order)
        
        print(f"Zamówienie {i+1}/{total_orders}: {order['product_name']} x{order['quantity']}")
        
        time.sleep(sleep_interval)
    
    print("Generowanie danych testowych zakończone!")
    print(f"Dane zapisane w: {log_file}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generator danych testowych dla ASEED Dashboard')
    parser.add_argument('--minutes', type=int, default=2, help='Czas generowania w minutach (domyślnie: 2)')
    parser.add_argument('--rate', type=int, default=6, help='Zamówienia na minutę (domyślnie: 6)')
    
    args = parser.parse_args()
    
    try:
        generate_test_data(args.minutes, args.rate)
    except KeyboardInterrupt:
        print("\n🛑 Zatrzymano przez użytkownika")
    except Exception as e:
        print(f"Błąd: {e}")
