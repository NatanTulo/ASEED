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
log_file = '/app/logs/order_simulator.log' if os.path.exists('/app/logs') else 'order_simulator.log'
logging.basicConfig(
    level=logging.INFO,  #ustawia minimalny poziom logów na INFO, czyli DEBUG nie będzie widoczny, a INFO, WARNING, ERROR i CRITICAL już tak
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', #format każdej linii w logu
    handlers=[
        logging.FileHandler(log_file)   #definiuje gdzie logi będą zapisywane
    ]
)
logger = logging.getLogger(__name__)

class OrderSimulator:
    def __init__(self):
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')   #adres brokera kafka
        self.topic = os.getenv('KAFKA_TOPIC', 'orders') # temat kafka, gdzie wysyłane są zamówienia
        # Częstość generowania zamówień - 3-8 sekund
        self.min_interval = float(os.getenv('MIN_ORDER_INTERVAL', '3'))  # min 3 sekundy
        self.max_interval = float(os.getenv('MAX_ORDER_INTERVAL', '8'))  # max 8 sekund
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
        
        # Konkretne produkty z konkretnymi, realistycznymi cenami
        product_list = [
            # Electronics
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
            
            # Clothing
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
            
            # Books
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
            
            # Home
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
            
            # Sports
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
            
            # Beauty
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
        
        # Twórz produkty z konkretnych definicji - przekształcenie surowej listy produktów w ustrukturyzowany format wymagany przez resztę aplikacji
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
        
        # Jeśli potrzebujemy więcej produktów, dodaj warianty. Z tego nie korzystamy, bo mamy 50 product_count i 60 products
        if len(products) < self.product_count:
            brands = ['Premium', 'Pro', 'Elite', 'Classic', 'Essential', 'Deluxe']
            colors = ['Black', 'White', 'Blue', 'Red', 'Silver', 'Gold']
            
            base_products = products.copy()
            while len(products) < self.product_count:
                base_product = random.choice(base_products)
                variant_name = f"{random.choice(brands)} {base_product['name']}"
                if random.choice([True, False]):
                    variant_name += f" - {random.choice(colors)}"
                
                # Warianty mają stałe mnożniki cenowe
                brand_multipliers = {
                    'Premium': 1.3, 'Pro': 1.25, 'Elite': 1.4, 
                    'Classic': 1.0, 'Essential': 0.8, 'Deluxe': 1.35
                }
                brand = variant_name.split()[0]
                multiplier = brand_multipliers.get(brand, 1.0)
                variant_price = round(base_product['base_price'] * multiplier, 2)
                
                product = {
                    'id': f'PROD-{len(products) + 1:03d}',
                    'name': variant_name,
                    'category': base_product['category'],
                    'base_price': variant_price
                }
                products.append(product)
        
        return products[:self.product_count]
    

    #system popularności produktów
    '''
    5 pierwszych produktów - bardzo popularne (waga 10)
    10 następnych produktów - średnio popularne (waga 5)
    Reszta produktów - mniej popularne (waga 1)
    '''


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
    

    #łączenie z kafka. 30 prób połączenia z Kafka, z 2-sekundowymi przerwami
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
        
        # Używaj stałej ceny produktu 
        final_price = product['base_price']
        

        #struktura zamówienia
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
            value = json.dumps(order).encode('utf-8')   #dict -> JSON string -> bytes (bo kafka operuje na surowych bajtach)
            key = order['order_id'].encode('utf-8')
            
            self.producer.produce(
                self.topic,   #'orders'
                key=key,      # b'ORDER-000001'  - klucz do decyzji, do której partycji trafi wiadomość
                value=value   # b'{"order_id": "ORDER-000001", ...}' (faktyczne dane zamówienia json)
            )
            # Prześlij natychmiast - flush wymusza wysłanie wszystkich oczekujących wiadomości
            self.producer.flush()
            
            logger.info(f"Wysłano zamówienie: {order['order_id']} - {order['product_name']} - ${order['price']}")
            return True
        except Exception as e:
            logger.error(f"Błąd wysyłania zamówienia {order['order_id']}: {e}")
            return False
    
    '''
    run() - główna pętla symulatora - generuje, wysyła zamówienie i potem sleep na randomowy czas od 3 to 8 sekund
    '''
    
    def run(self):
        """Główna pętla symulatora"""
        logger.info("Rozpoczynanie symulatora zamówień...")
        logger.info(f"Wysyłanie zamówień w losowych odstępach {self.min_interval}-{self.max_interval} sekund")
        
        self._connect_kafka()
        
        try:
            while self.running:
                # Generuj i wyślij zamówienie
                order = self._generate_order()
                self.send_order(order)
                
                # Losowy czas oczekiwania między zamówieniami (3-8 sekund)
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
