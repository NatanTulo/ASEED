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

log_file = '/app/logs/order_simulator.log' if os.path.exists('/app/logs') else 'order_simulator.log'
logging.basicConfig(
    level=logging.INFO,                                                                                                                     
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',                            
    handlers=[
        logging.FileHandler(log_file)                                        
    ]
)
logger = logging.getLogger(__name__)

class OrderSimulator:
    def __init__(self):
        # Konfiguracja z env
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = os.getenv('KAFKA_TOPIC', 'orders')
        self.product_count = int(os.getenv('PRODUCT_COUNT', '50'))

        # Stałe sterowanie tempem poprzez MIN/MAX
        try:
            self.min_interval = float(os.getenv('MIN_ORDER_INTERVAL', '3'))
            self.max_interval = float(os.getenv('MAX_ORDER_INTERVAL', '8'))
            if self.min_interval <= 0 or self.max_interval <= 0 or self.min_interval > self.max_interval:
                raise ValueError
        except ValueError:
            logger.warning("Niepoprawne wartości MIN/MAX – używam domyślnych 3..8s")
            self.min_interval = 3.0
            self.max_interval = 8.0

        self.fake = Faker()
        self.producer = None
        self.order_counter = 0
        self.running = True

        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.products = self._generate_products()
        self.product_weights = self._generate_product_weights()

    def _signal_handler(self, signum, frame):
        """Obsługa sygnałów do graceful shutdown"""
        logger.info(f"Otrzymano sygnał {signum}. Zatrzymywanie symulatora...")
        self.running = False

    def _generate_products(self):
        """Generuje listę produktów"""
        products = []

        product_list = [
            {'name': 'Wireless Bluetooth Headphones', 'category': 'Electronics', 'price': 79.99},
            {'name': 'Smart LED TV', 'category': 'Electronics', 'price': 649.99},
            {'name': 'Gaming Mechanical Keyboard', 'category': 'Electronics', 'price': 129.99},
            {'name': 'USB-C Power Bank', 'category': 'Electronics', 'price': 39.99},
            {'name': 'Smartphone Case', 'category': 'Electronics', 'price': 24.99},
            {'name': 'Wireless Charging Pad', 'category': 'Electronics', 'price': 34.99},
            {'name': 'Bluetooth Speaker', 'category': 'Electronics', 'price': 89.99},
            {'name': 'Digital Camera', 'category': 'Electronics', 'price': 449.99},
            {'name': 'Laptop Stand', 'category': 'Electronics', 'price': 59.99},
            {'name': 'Smart Watch', 'category': 'Electronics', 'price': 299.99},

            {'name': 'Cotton T-Shirt', 'category': 'Clothing', 'price': 19.99},
            {'name': 'Denim Jeans', 'category': 'Clothing', 'price': 69.99},
            {'name': 'Winter Jacket', 'category': 'Clothing', 'price': 149.99},
            {'name': 'Running Sneakers', 'category': 'Clothing', 'price': 119.99},
            {'name': 'Wool Sweater', 'category': 'Clothing', 'price': 79.99},
            {'name': 'Leather Boots', 'category': 'Clothing', 'price': 159.99},
            {'name': 'Summer Dress', 'category': 'Clothing', 'price': 49.99},
            {'name': 'Baseball Cap', 'category': 'Clothing', 'price': 24.99},
            {'name': 'Casual Hoodie', 'category': 'Clothing', 'price': 59.99},
            {'name': 'Canvas Backpack', 'category': 'Clothing', 'price': 89.99},

            {'name': 'Programming Guide', 'category': 'Books', 'price': 39.99},
            {'name': 'Mystery Novel', 'category': 'Books', 'price': 14.99},
            {'name': 'Science Fiction Book', 'category': 'Books', 'price': 16.99},
            {'name': 'Cookbook', 'category': 'Books', 'price': 29.99},
            {'name': 'History Encyclopedia', 'category': 'Books', 'price': 49.99},
            {'name': 'Self-Help Book', 'category': 'Books', 'price': 22.99},
            {'name': 'Art Album', 'category': 'Books', 'price': 44.99},
            {'name': 'Travel Guide', 'category': 'Books', 'price': 26.99},
            {'name': 'Biography', 'category': 'Books', 'price': 19.99},
            {'name': 'Poetry Collection', 'category': 'Books', 'price': 12.99},

            {'name': 'Coffee Maker', 'category': 'Home', 'price': 179.99},
            {'name': 'Table Lamp', 'category': 'Home', 'price': 69.99},
            {'name': 'Throw Pillow', 'category': 'Home', 'price': 29.99},
            {'name': 'Kitchen Knife Set', 'category': 'Home', 'price': 89.99},
            {'name': 'Ceramic Vase', 'category': 'Home', 'price': 39.99},
            {'name': 'Wall Clock', 'category': 'Home', 'price': 49.99},
            {'name': 'Storage Box', 'category': 'Home', 'price': 34.99},
            {'name': 'Candle Set', 'category': 'Home', 'price': 24.99},
            {'name': 'Picture Frame', 'category': 'Home', 'price': 19.99},
            {'name': 'Bed Sheets', 'category': 'Home', 'price': 54.99},

            {'name': 'Yoga Mat', 'category': 'Sports', 'price': 34.99},
            {'name': 'Dumbbells Set', 'category': 'Sports', 'price': 149.99},
            {'name': 'Tennis Racket', 'category': 'Sports', 'price': 89.99},
            {'name': 'Basketball', 'category': 'Sports', 'price': 24.99},
            {'name': 'Running Shoes', 'category': 'Sports', 'price': 129.99},
            {'name': 'Fitness Tracker', 'category': 'Sports', 'price': 199.99},
            {'name': 'Water Bottle', 'category': 'Sports', 'price': 18.99},
            {'name': 'Gym Bag', 'category': 'Sports', 'price': 44.99},
            {'name': 'Exercise Ball', 'category': 'Sports', 'price': 29.99},
            {'name': 'Resistance Bands', 'category': 'Sports', 'price': 22.99},

            {'name': 'Face Moisturizer', 'category': 'Beauty', 'price': 32.99},
            {'name': 'Lip Balm', 'category': 'Beauty', 'price': 7.99},
            {'name': 'Shampoo', 'category': 'Beauty', 'price': 16.99},
            {'name': 'Perfume', 'category': 'Beauty', 'price': 79.99},
            {'name': 'Makeup Brush Set', 'category': 'Beauty', 'price': 49.99},
            {'name': 'Sunscreen', 'category': 'Beauty', 'price': 19.99},
            {'name': 'Hair Conditioner', 'category': 'Beauty', 'price': 18.99},
            {'name': 'Face Mask', 'category': 'Beauty', 'price': 12.99},
            {'name': 'Nail Polish', 'category': 'Beauty', 'price': 9.99},
            {'name': 'Essential Oil', 'category': 'Beauty', 'price': 24.99}
        ]

        for i, product_data in enumerate(product_list):
            if i >= self.product_count:
                break

            product = {
                'id': f'PROD-{i + 1:03d}',
                'name': product_data['name'],
                'category': product_data['category'],
                'base_price': product_data['price']
            }
            products.append(product)


        return products[:self.product_count]


    def _generate_product_weights(self):
        """Generuje wagi dla produktów - niektóre będą popularniejsze"""
        weights = []
        for i in range(len(self.products)):
            if i < 5:                                                    
                weights.append(10)
            elif i < 15:                                            
                weights.append(5)
            else:                                 
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

        product = random.choices(self.products, weights=self.product_weights)[0]

        final_price = product['base_price']


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
            value = json.dumps(order).encode('utf-8')                                                                       
            key = order['order_id'].encode('utf-8')
            if not self.producer:
                logger.error("Producer Kafka nie jest zainicjalizowany")
                return False
            self.producer.produce(self.topic, key=key, value=value)
            self.producer.flush()

            logger.info(f"Wysłano zamówienie: {order['order_id']} - {order['product_name']} - ${order['price']}")
            return True
        except Exception as e:
            logger.error(f"Błąd wysyłania zamówienia {order['order_id']}: {e}")
            return False

    def run(self):
        """Główna pętla symulatora"""
        logger.info("Rozpoczynanie symulatora zamówień...")
        logger.info(f"Wysyłanie zamówień w losowych odstępach {self.min_interval}-{self.max_interval} sekund")
        logger.info(f"Kafka: {self.kafka_servers} | Topic: {self.topic} | Produkty: {self.product_count}")

        self._connect_kafka()

        try:
            while self.running:
                order = self._generate_order()
                self.send_order(order)

                sleep_time = random.uniform(self.min_interval, self.max_interval)
                logger.debug(f"Czekam {sleep_time:.1f} sekund do następnego zamówienia...")
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
                self.producer.flush(timeout=5)
                self.producer.close()
                logger.info("Zamknięto połączenie z Kafka")
            except Exception as e:
                logger.warning(f"Błąd podczas zamykania producenta Kafka: {e}")

def main():
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