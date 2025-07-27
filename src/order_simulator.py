import json
import time
import random
import os
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
        
        # Produkty z różnymi prawdopodobieństwami (niektóre produkty będą popularne)
        self.products = self._generate_products()
        self.product_weights = self._generate_product_weights()
        
    def _generate_products(self):
        """Generuje listę produktów"""
        products = []
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty']
        
        for i in range(1, self.product_count + 1):
            category = random.choice(categories)
            product = {
                'id': f'PROD-{i:03d}',
                'name': f'{category} {self.fake.word().title()} {i}',
                'category': category,
                'base_price': round(random.uniform(5.99, 299.99), 2)
            }
            products.append(product)
        return products
    
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
            while True:
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
            if self.producer:
                self.producer.close()
                logger.info("Zamknięto połączenie z Kafka")

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
