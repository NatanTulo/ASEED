import os
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrderAnalyzer:
    def __init__(self):
        self.spark_master = os.getenv('SPARK_MASTER_URL', 'local[*]')
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.kafka_topic = os.getenv('KAFKA_TOPIC', 'orders')
        
        self.spark = None
        
    def _create_spark_session(self):
        """Tworzy sesję Spark"""
        try:
            # Dla lokalnego uruchomienia używamy local[*]
            self.spark = SparkSession.builder \
                .appName("OrderAnalysis") \
                .master(self.spark_master) \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
                .getOrCreate()
            
            self.spark.sparkContext.setLogLevel("WARN")
            logger.info(f"Utworzono sesję Spark: {self.spark_master}")
            
        except Exception as e:
            logger.error(f"Błąd tworzenia sesji Spark: {e}")
            raise
    
    def _define_schema(self):
        """Definiuje schemat danych zamówienia"""
        return StructType([
            StructField("order_id", StringType(), True),
            StructField("product_id", StringType(), True),
            StructField("product_name", StringType(), True),
            StructField("category", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("quantity", IntegerType(), True),
            StructField("customer_id", StringType(), True),
            StructField("timestamp", StringType(), True)
        ])
    
    def _read_kafka_stream(self):
        """Czyta strumień danych z Kafka"""
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                df = self.spark \
                    .readStream \
                    .format("kafka") \
                    .option("kafka.bootstrap.servers", self.kafka_servers) \
                    .option("subscribe", self.kafka_topic) \
                    .option("startingOffsets", "latest") \
                    .option("failOnDataLoss", "false") \
                    .load()
                
                logger.info(f"Podłączono do Kafka topic: {self.kafka_topic}")
                return df
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Próba połączenia z Kafka {retry_count}/{max_retries}: {e}")
                if retry_count < max_retries:
                    time.sleep(2)
                else:
                    logger.error("Nie udało się połączyć z Kafka po wszystkich próbach")
                    raise
    
    def _parse_orders(self, kafka_df):
        """Parsuje dane zamówień z JSON"""
        schema = self._define_schema()
        
        orders_df = kafka_df \
            .select(from_json(col("value").cast("string"), schema).alias("order")) \
            .select("order.*") \
            .withColumn("timestamp_parsed", to_timestamp(col("timestamp"))) \
            .withColumn("total_value", col("price") * col("quantity"))
        
        return orders_df
    
    def _analyze_top_products(self, orders_df):
        """Analizuje top produkty w oknie czasowym"""
        
        # Analiza w oknie 1 minuty z aktualizacją co 10 sekund
        windowed_analysis = orders_df \
            .withWatermark("timestamp_parsed", "30 seconds") \
            .groupBy(
                window(col("timestamp_parsed"), "1 minute", "10 seconds"),
                col("product_id"),
                col("product_name"),
                col("category")
            ) \
            .agg(
                count("order_id").alias("order_count"),
                sum("quantity").alias("total_quantity"),
                sum("total_value").alias("total_revenue"),
                avg("price").alias("avg_price")
            ) \
            .withColumn("window_start", col("window.start")) \
            .withColumn("window_end", col("window.end")) \
            .drop("window")
        
        return windowed_analysis
    
    def _analyze_categories(self, orders_df):
        """Analizuje sprzedaż po kategoriach"""
        
        category_analysis = orders_df \
            .withWatermark("timestamp_parsed", "30 seconds") \
            .groupBy(
                window(col("timestamp_parsed"), "1 minute", "10 seconds"),
                col("category")
            ) \
            .agg(
                count("order_id").alias("order_count"),
                sum("quantity").alias("total_quantity"),
                sum("total_value").alias("total_revenue"),
                approx_count_distinct("product_id").alias("unique_products")
            ) \
            .withColumn("window_start", col("window.start")) \
            .withColumn("window_end", col("window.end")) \
            .drop("window")
        
        return category_analysis
    
    def _output_top_products(self, analysis_df):
        """Wyprowadza wyniki analizy produktów"""
        
        def process_batch(batch_df, batch_id):
            if batch_df.count() > 0:
                logger.info(f"\n{'='*80}")
                logger.info(f"TOP PRODUKTY - Batch {batch_id}")
                logger.info(f"{'='*80}")
                
                # Pokaż top 10 produktów według liczby zamówień
                top_products = batch_df \
                    .orderBy(desc("order_count"), desc("total_revenue")) \
                    .limit(10)
                
                products_list = top_products.collect()
                
                for i, row in enumerate(products_list, 1):
                    logger.info(f"{i:2d}. {row['product_name']}")
                    logger.info(f"    Kategoria: {row['category']}")
                    logger.info(f"    Zamówienia: {row['order_count']}, Ilość: {row['total_quantity']}")
                    logger.info(f"    Przychód: ${row['total_revenue']:.2f}, Śr. cena: ${row['avg_price']:.2f}")
                    logger.info(f"    Okno: {row['window_start']} - {row['window_end']}")
                    logger.info("")
        
        query = analysis_df.writeStream \
            .foreachBatch(process_batch) \
            .outputMode("complete") \
            .trigger(processingTime='10 seconds') \
            .start()
        
        return query
    
    def _output_categories(self, analysis_df):
        """Wyprowadza wyniki analizy kategorii"""
        
        def process_batch(batch_df, batch_id):
            if batch_df.count() > 0:
                logger.info(f"\n{'='*80}")
                logger.info(f"ANALIZA KATEGORII - Batch {batch_id}")
                logger.info(f"{'='*80}")
                
                categories = batch_df \
                    .orderBy(desc("total_revenue")) \
                    .collect()
                
                for row in categories:
                    logger.info(f"Kategoria: {row['category']}")
                    logger.info(f"  Zamówienia: {row['order_count']}, Produkty: {row['unique_products']}")
                    logger.info(f"  Przychód: ${row['total_revenue']:.2f}")
                    logger.info(f"  Okno: {row['window_start']} - {row['window_end']}")
                    logger.info("")
        
        query = analysis_df.writeStream \
            .foreachBatch(process_batch) \
            .outputMode("complete") \
            .trigger(processingTime='15 seconds') \
            .start()
        
        return query
    
    def run(self):
        """Główna metoda uruchamiająca analizę"""
        logger.info("Rozpoczynanie analizy zamówień...")
        
        self._create_spark_session()
        
        # Czytaj dane z Kafka
        kafka_df = self._read_kafka_stream()
        
        # Parsuj zamówienia
        orders_df = self._parse_orders(kafka_df)
        
        # Przeprowadź analizy
        product_analysis = self._analyze_top_products(orders_df)
        category_analysis = self._analyze_categories(orders_df)
        
        # Uruchom strumienie wyjściowe
        product_query = self._output_top_products(product_analysis)
        category_query = self._output_categories(category_analysis)
        
        try:
            # Czekaj na zakończenie
            product_query.awaitTermination()
            category_query.awaitTermination()
            
        except KeyboardInterrupt:
            logger.info("Zatrzymywanie analizy...")
            product_query.stop()
            category_query.stop()
            
        finally:
            if self.spark:
                self.spark.stop()
                logger.info("Zamknięto sesję Spark")

def main():
    # Załaduj konfigurację z pliku .env jeśli istnieje
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    analyzer = OrderAnalyzer()
    analyzer.run()

if __name__ == "__main__":
    main()
