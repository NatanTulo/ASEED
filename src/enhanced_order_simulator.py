#!/usr/bin/env python3
"""
Enhanced Order Simulator z realistycznymi wzorcami e-commerce
- Promocje flash i sezonowe
- Wzorce zachowań klientów  
- Segmenty klientów
- Symulacja stanu magazynowego
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
from faker import Faker
import logging
import signal
import sys

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rozszerzony katalog produktów z inwentarzem
ENHANCED_PRODUCTS = [
    # Electronics - wysokowartościowe, flash sales
    {"id": "ELEC001", "name": "Premium Wireless Headphones", "category": "Electronics", "base_price": 299.99, "inventory": 50, "flash_sale": True},
    {"id": "ELEC002", "name": "4K Gaming Monitor", "category": "Electronics", "base_price": 449.99, "inventory": 30, "flash_sale": False},
    {"id": "ELEC003", "name": "Smartphone Pro Max", "category": "Electronics", "base_price": 999.99, "inventory": 25, "flash_sale": True},
    {"id": "ELEC004", "name": "Wireless Charging Station", "category": "Electronics", "base_price": 89.99, "inventory": 100, "flash_sale": False},
    {"id": "ELEC005", "name": "Bluetooth Speaker", "category": "Electronics", "base_price": 129.99, "inventory": 75, "flash_sale": True},
    
    # Fashion - trendy sezonowe
    {"id": "FASH001", "name": "Summer Dress Collection", "category": "Fashion", "base_price": 79.99, "inventory": 100, "seasonal": True},
    {"id": "FASH002", "name": "Designer Sneakers", "category": "Fashion", "base_price": 159.99, "inventory": 75, "seasonal": False},
    {"id": "FASH003", "name": "Leather Jacket", "category": "Fashion", "base_price": 249.99, "inventory": 40, "seasonal": True},
    {"id": "FASH004", "name": "Casual T-Shirt", "category": "Fashion", "base_price": 29.99, "inventory": 200, "seasonal": False},
    {"id": "FASH005", "name": "Winter Coat", "category": "Fashion", "base_price": 199.99, "inventory": 60, "seasonal": True},
    
    # Home & Garden - zakupy hurtowe
    {"id": "HOME001", "name": "Smart Home Security Kit", "category": "Home", "base_price": 199.99, "inventory": 40, "bulk_discount": True},
    {"id": "HOME002", "name": "Organic Garden Starter Set", "category": "Home", "base_price": 49.99, "inventory": 200, "seasonal": True},
    {"id": "HOME003", "name": "Coffee Machine Premium", "category": "Home", "base_price": 299.99, "inventory": 35, "bulk_discount": False},
    {"id": "HOME004", "name": "Kitchen Blender Set", "category": "Home", "base_price": 89.99, "inventory": 80, "bulk_discount": True},
    {"id": "HOME005", "name": "LED Floor Lamp", "category": "Home", "base_price": 129.99, "inventory": 65, "bulk_discount": False},
    
    # Books - stabilny popyt
    {"id": "BOOK001", "name": "Machine Learning Handbook", "category": "Books", "base_price": 39.99, "inventory": 500, "educational": True},
    {"id": "BOOK002", "name": "Cooking Masterclass Guide", "category": "Books", "base_price": 24.99, "inventory": 300, "trending": True},
    {"id": "BOOK003", "name": "Data Science for Beginners", "category": "Books", "base_price": 34.99, "inventory": 400, "educational": True},
    {"id": "BOOK004", "name": "Photography Essentials", "category": "Books", "base_price": 29.99, "inventory": 250, "trending": False},
    {"id": "BOOK005", "name": "Business Strategy Guide", "category": "Books", "base_price": 44.99, "inventory": 180, "educational": True},
    
    # Sports - sezonowo i trendowo
    {"id": "SPRT001", "name": "Professional Running Shoes", "category": "Sports", "base_price": 159.99, "inventory": 90, "seasonal": True},
    {"id": "SPRT002", "name": "Yoga Mat Premium", "category": "Sports", "base_price": 49.99, "inventory": 120, "seasonal": False},
    {"id": "SPRT003", "name": "Fitness Tracker", "category": "Sports", "base_price": 199.99, "inventory": 70, "trending": True},
    {"id": "SPRT004", "name": "Basketball Official", "category": "Sports", "base_price": 39.99, "inventory": 150, "seasonal": True},
    {"id": "SPRT005", "name": "Swimming Goggles Pro", "category": "Sports", "base_price": 29.99, "inventory": 200, "seasonal": True},
    
    # Beauty - regularne promocje
    {"id": "BEAU001", "name": "Skincare Set Deluxe", "category": "Beauty", "base_price": 89.99, "inventory": 85, "promotional": True},
    {"id": "BEAU002", "name": "Hair Care Collection", "category": "Beauty", "base_price": 59.99, "inventory": 110, "promotional": True},
    {"id": "BEAU003", "name": "Makeup Brush Set", "category": "Beauty", "base_price": 79.99, "inventory": 95, "promotional": False},
    {"id": "BEAU004", "name": "Perfume Luxury", "category": "Beauty", "base_price": 149.99, "inventory": 45, "promotional": True},
    {"id": "BEAU005", "name": "Face Mask Bundle", "category": "Beauty", "base_price": 34.99, "inventory": 160, "promotional": True},
]

class EnhancedOrderSimulator:
    def __init__(self):
        # Konfiguracja Kafka
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = os.getenv('KAFKA_TOPIC', 'orders')
        
        # Konfiguracja timingu
        self.min_interval = float(os.getenv('MIN_ORDER_INTERVAL', '3'))  # min 3 sekundy
        self.max_interval = float(os.getenv('MAX_ORDER_INTERVAL', '8'))  # max 8 sekund
        
        self.fake = Faker()
        self.producer = None
        self.order_counter = 0
        self.running = True
        
        # Ustawienie obsługi sygnałów
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Segmenty klientów
        self.customer_segments = {
            'premium': {'probability': 0.2, 'avg_order_value': 200, 'loyalty': 0.8},
            'regular': {'probability': 0.6, 'avg_order_value': 75, 'loyalty': 0.5}, 
            'bargain': {'probability': 0.2, 'avg_order_value': 30, 'loyalty': 0.3}
        }
        
        # Wzorce godzinowe (mnożniki aktywności)
        self.hourly_multipliers = {
            0: 0.1, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.05, 5: 0.1,
            6: 0.2, 7: 0.4, 8: 0.6, 9: 0.8, 10: 1.0, 11: 1.2,
            12: 1.5, 13: 1.3, 14: 1.1, 15: 1.0, 16: 0.9, 17: 0.8,
            18: 1.2, 19: 1.4, 20: 1.6, 21: 1.3, 22: 0.8, 23: 0.4
        }
        
        logger.info("Enhanced Order Simulator zainicjalizowany z realistycznymi wzorcami")
    
    def _signal_handler(self, signum, frame):
        """Obsługa sygnałów do graceful shutdown"""
        logger.info(f"Otrzymano sygnał {signum}. Zatrzymywanie symulatora...")
        self.running = False

    def _connect_kafka(self):
        """Nawiązuje połączenie z Kafka"""
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.kafka_servers.split(','),
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                    key_serializer=lambda x: x.encode('utf-8') if x else None,
                    retries=5,
                    retry_backoff_ms=1000
                )
                logger.info(f"Połączono z Kafka: {self.kafka_servers}")
                return
            except Exception as e:
                retry_count += 1
                logger.warning(f"Próba połączenia z Kafka {retry_count}/{max_retries}: {e}")
                if retry_count < max_retries:
                    time.sleep(2)
                else:
                    logger.error("Nie udało się połączyć z Kafka po wszystkich próbach")
                    raise

    def get_current_promotions(self):
        """Pobierz aktywne promocje na podstawie czasu i inwentarza"""
        current_hour = datetime.now().hour  
        promotions = []
        
        # Flash sales podczas godzin szczytu
        if 12 <= current_hour <= 14 or 18 <= current_hour <= 21:
            flash_products = [p for p in ENHANCED_PRODUCTS if p.get('flash_sale')]
            if flash_products:
                promotions.extend(flash_products)
        
        # Promocje sezonowe
        current_month = datetime.now().month
        if current_month in [6, 7, 8]:  # Lato
            seasonal_products = [p for p in ENHANCED_PRODUCTS if p.get('seasonal')]
            promotions.extend(seasonal_products)
        elif current_month in [12, 1, 2]:  # Zima
            winter_products = [p for p in ENHANCED_PRODUCTS if p.get('seasonal') and 'Winter' in p['name']]
            promotions.extend(winter_products)
            
        return promotions

    def generate_enhanced_order(self):
        """Generuj zamówienie z realistycznymi wzorcami e-commerce"""
        
        # Wybierz segment klienta
        segment_rand = random.random()
        if segment_rand < 0.2:
            segment = 'premium'
        elif segment_rand < 0.8:
            segment = 'regular'  
        else:
            segment = 'bargain'
            
        customer_profile = self.customer_segments[segment]
        
        # Zastosuj wzorce czasowe zamówień
        current_hour = datetime.now().hour
        order_probability = self.hourly_multipliers.get(current_hour, 1.0)
        
        if random.random() > order_probability:
            return None  # Pomiń zamówienie na podstawie wzorców czasowych
            
        # Wybierz produkt na podstawie promocji i segmentu
        promotions = self.get_current_promotions()
        
        if promotions and random.random() < 0.4:  # 40% szans na kupno promowanych produktów
            product = random.choice(promotions)
            price_multiplier = 0.8  # 20% zniżki
        else:
            product = random.choice(ENHANCED_PRODUCTS)
            price_multiplier = 1.0
            
        # Klienci premium kupują droższe produkty
        if segment == 'premium' and product['base_price'] < 100:
            expensive_products = [p for p in ENHANCED_PRODUCTS if p['base_price'] > 100]
            if expensive_products:
                product = random.choice(expensive_products)
        
        # Generuj realistyczną ilość na podstawie typu produktu i klienta
        if product['category'] == 'Electronics':
            quantity = 1  # Zazwyczaj pojedyncze przedmioty
        elif product.get('bulk_discount'):
            quantity = random.choices([1, 2, 3, 5], weights=[0.4, 0.3, 0.2, 0.1])[0]
        else:
            quantity = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            
        # Oblicz cenę końcową z promocjami i zniżkami ilościowymi
        final_price = product['base_price'] * price_multiplier
        if quantity >= 3:
            final_price *= 0.95  # 5% zniżka hurtowa
            
        # Wygeneruj zamówienie
        self.order_counter += 1
        order = {
            'order_id': f"ORD-{self.order_counter:06d}",
            'product_id': product['id'],
            'product_name': product['name'],
            'category': product['category'],
            'price': round(final_price, 2),
            'quantity': quantity,
            'total_value': round(final_price * quantity, 2),
            'customer_id': f"CUST-{random.randint(1000, 9999):04d}",
            'customer_segment': segment,
            'promotion_applied': price_multiplier < 1.0,
            'timestamp': datetime.now().isoformat(),
        }
        
        return order

    def send_order(self, order):
        """Wyślij zamówienie do Kafka"""
        try:
            self.producer.send(
                self.topic,
                value=order,
                key=order['order_id']
            )
            # Flush natychmiast
            self.producer.flush()
            
            logger.info(f"Wysłano zamówienie: {order['order_id']} - {order['product_name']} - ${order['price']} x{order['quantity']}")
            return True
        except Exception as e:
            logger.error(f"Błąd wysyłania zamówienia {order['order_id']}: {e}")
            return False

    def run(self):
        """Główna pętla symulatora"""
        logger.info("🚀 Rozpoczynanie Enhanced Order Simulator z realistycznymi wzorcami...")
        logger.info(f"📊 Funkcje: Flash sales, segmenty klientów, wzorce czasowe, zniżki hurtowe")
        logger.info(f"📡 Wysyłanie do Kafka: {self.kafka_servers} topic: {self.topic}")
        
        self._connect_kafka()
        
        try:
            order_count = 0
            while self.running:
                start_time = time.time()
                
                order = self.generate_enhanced_order()
                
                if order:  # Zamówienie może być None ze względu na wzorce czasowe
                    if self.send_order(order):
                        order_count += 1
                        
                        if order_count % 10 == 0:
                            logger.info(f"📦 Wysłano {order_count} enhanced orders")
                
                # Oblicz czas czekania z małą randomizacją
                interval = random.uniform(self.min_interval, self.max_interval)
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logger.info("Zatrzymywanie symulatora...")
        except Exception as e:
            logger.error(f"Błąd w symulatorze: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Bezpieczne zamykanie symulatora"""
        logger.info("Zamykanie Enhanced Order Simulator...")
        if self.producer:
            try:
                self.producer.flush(timeout=5)
                self.producer.close()
                logger.info("Zamknięto połączenie z Kafka")
            except Exception as e:
                logger.warning(f"Błąd podczas zamykania producenta Kafka: {e}")

def main():
    # Załaduj konfigurację z pliku .env jeśli istnieje
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

    simulator = EnhancedOrderSimulator()
    simulator.run()

if __name__ == '__main__':
    main()
