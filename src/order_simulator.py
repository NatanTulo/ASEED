import json
import time
import random
import os
import signal
import sys
from datetime import datetime
from confluent_kafka import Producer
from faker import Faker
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrderSimulator:
    def __init__(self):
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = os.getenv('KAFKA_TOPIC', 'orders')
        self.orders_per_second = float(os.getenv('ORDERS_PER_SECOND', '2'))
        self.product_count = int(os.getenv('PRODUCT_COUNT', '50'))
        
        self.fake = Faker()
        self.producer = None
        self.order_counter = 0
        self.running = True
        
        # Ustawienie obsługi sygnałów
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Produkty z różnymi prawdopodobieństwami (niektóre produkty będą popularne)
        self.products = self._generate_products()
        self.product_weights = self._generate_product_weights()
    
    def _signal_handler(self, signum, frame):
        """Obsługa sygnałów do graceful shutdown"""
        logger.info(f"Otrzymano sygnał {signum}. Zatrzymywanie symulatora...")
        self.running = False
        
    def _generate_products(self):
        """Generuje listę produktów"""
        products = []
        
        # Realistyczne produkty dla każdej kategorii
        product_templates = {
            'Electronics': [
                'Wireless Bluetooth Headphones', 'Smart LED TV', 'Gaming Mechanical Keyboard',
                'USB-C Power Bank', 'Smartphone Case', 'Wireless Charging Pad',
                'Bluetooth Speaker', 'Digital Camera', 'Laptop Stand', 'Smart Watch'
            ],
            'Clothing': [
                'Cotton T-Shirt', 'Denim Jeans', 'Winter Jacket', 'Running Sneakers',
                'Wool Sweater', 'Leather Boots', 'Summer Dress', 'Baseball Cap',
                'Casual Hoodie', 'Canvas Backpack'
            ],
            'Books': [
                'Programming Guide', 'Mystery Novel', 'Science Fiction Book', 'Cookbook',
                'History Encyclopedia', 'Self-Help Book', 'Art Album', 'Travel Guide',
                'Biography', 'Poetry Collection'
            ],
            'Home': [
                'Coffee Maker', 'Table Lamp', 'Throw Pillow', 'Kitchen Knife Set',
                'Ceramic Vase', 'Wall Clock', 'Storage Box', 'Candle Set',
                'Picture Frame', 'Bed Sheets'
            ],
            'Sports': [
                'Yoga Mat', 'Dumbbells Set', 'Tennis Racket', 'Basketball',
                'Running Shoes', 'Fitness Tracker', 'Water Bottle', 'Gym Bag',
                'Exercise Ball', 'Resistance Bands'
            ],
            'Beauty': [
                'Face Moisturizer', 'Lip Balm', 'Shampoo', 'Perfume',
                'Makeup Brush Set', 'Sunscreen', 'Hair Conditioner', 'Face Mask',
                'Nail Polish', 'Essential Oil'
            ]
        }
        
        # Generuj produkty używając predefiniowanych nazw
        product_id = 1
        for category, product_names in product_templates.items():
            for name in product_names:
                if product_id > self.product_count:
                    break
                    
                product = {
                    'id': f'PROD-{product_id:03d}',
                    'name': name,
                    'category': category,
                    'base_price': round(random.uniform(5.99, 299.99), 2)
                }
                products.append(product)
                product_id += 1
                
            if product_id > self.product_count:
                break
        
        # Jeśli potrzebujemy więcej produktów, dodaj warianty z markami/modelami
        if len(products) < self.product_count:
            brands = ['Premium', 'Pro', 'Elite', 'Classic', 'Essential', 'Deluxe']
            colors = ['Black', 'White', 'Blue', 'Red', 'Silver', 'Gold']
            
            base_products = products.copy()
            while len(products) < self.product_count:
                base_product = random.choice(base_products)
                variant_name = f"{random.choice(brands)} {base_product['name']}"
                if random.choice([True, False]):
                    variant_name += f" - {random.choice(colors)}"
                
                product = {
                    'id': f'PROD-{len(products) + 1:03d}',
                    'name': variant_name,
                    'category': base_product['category'],
                    'base_price': round(base_product['base_price'] * random.uniform(0.8, 1.5), 2)
                }
                products.append(product)
        
        return products[:self.product_count]  # Zwróć dokładnie tyle ile potrzeba
    
    def _generate_product_weights(self):
        """Generuje wagi dla produktów - niektóre będą popularniejsze"""
        weights = []
        for i in range(len(self.products)):
            if i < 5:  # Pierwszych 5 produktów będzie bardzo popularnych
                weights.append(10)
            elif i < 15:  # Następnych 10 będzie średnio popularnych
                weights.append(5)
            else:  # Reszta będzie mniej popularna
                weights.append(1)
        return weights
    
    def _connect_kafka(self):
        """Nawiązuje połączenie z Kafka"""
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.producer = Producer({
                    'bootstrap.servers': self.kafka_servers,
                    'retries': 5,
                    'retry.backoff.ms': 1000
                })
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
    
    def _generate_order(self):
        """Generuje pojedyncze zamówienie"""
        self.order_counter += 1
        
        # Wybierz produkt na podstawie wag (popularności)
        product = random.choices(self.products, weights=self.product_weights)[0]
        
        # Dodaj losową wariację do ceny bazowej
        price_variation = random.uniform(0.8, 1.2)
        final_price = round(product['base_price'] * price_variation, 2)
        
        order = {
            'order_id': f'ORDER-{self.order_counter:06d}',
            'product_id': product['id'],
            'product_name': product['name'],
            'category': product['category'],
            'price': final_price,
            'quantity': random.randint(1, 5),
            'customer_id': f'CUST-{random.randint(1, 1000):04d}',
            'timestamp': datetime.now().isoformat()
        }
        
        return order
    
    def send_order(self, order):
        """Wysyła zamówienie do Kafka"""
        try:
            # Serializuj do JSON
            value = json.dumps(order).encode('utf-8')
            key = order['order_id'].encode('utf-8')
            
            self.producer.produce(
                self.topic,
                key=key,
                value=value
            )
            # Prześlij natychmiast
            self.producer.flush()
            
            logger.info(f"Wysłano zamówienie: {order['order_id']} - {order['product_name']} - ${order['price']}")
            return True
        except Exception as e:
            logger.error(f"Błąd wysyłania zamówienia {order['order_id']}: {e}")
            return False
    
    def run(self):
        """Główna pętla symulatora"""
        logger.info("Rozpoczynanie symulatora zamówień...")
        logger.info(f"Wysyłanie {self.orders_per_second} zamówień na sekundę do topiku '{self.topic}'")
        
        self._connect_kafka()
        
        interval = 1.0 / self.orders_per_second
        
        try:
            while self.running:
                start_time = time.time()
                
                order = self._generate_order()
                self.send_order(order)
                
                # Oblicz ile czasu zająć powinno czekanie
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
        logger.info("Zamykanie symulatora...")
        if self.producer:
            try:
                # Poczekaj na wysłanie wszystkich wiadomości
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
    
    simulator = OrderSimulator()
    simulator.run()

if __name__ == "__main__":
    main()
