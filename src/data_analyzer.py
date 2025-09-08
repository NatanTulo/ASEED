import os
import time
import signal
import sys
import json
import requests
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging

log_file = '/logs/data_analyzer.log' if os.path.exists('/logs') else 'data_analyzer.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)

class OrderAnalyzer:
    def __init__(self):
        self.spark_master = os.getenv('SPARK_MASTER_URL', 'local[*]')
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
        self.kafka_topic = os.getenv('KAFKA_TOPIC', 'orders')
        self.dashboard_url = os.getenv('DASHBOARD_URL', 'http://web-dashboard:5005')

        # Interwały batch (parametryzowane przez .env)
        def _read_interval(name: str, default: int) -> int:
            raw = os.getenv(name, str(default)).strip()
            try:
                val = int(raw)
                if val <= 0:
                    raise ValueError
                return val
            except ValueError:
                logger.warning(f"Niepoprawna wartość {name}={raw} – używam domyślnej {default}s")
                return default

        self.top_products_interval = _read_interval('TOP_PRODUCTS_INTERVAL_SECONDS', 10)
        self.categories_interval = _read_interval('CATEGORIES_INTERVAL_SECONDS', 15)
        self.raw_orders_interval = _read_interval('RAW_ORDERS_INTERVAL_SECONDS', 5)

        logger.info(
            "Interwały batch: top_products=%ss, categories=%ss, raw_orders=%ss", 
            self.top_products_interval, self.categories_interval, self.raw_orders_interval
        )

        self.spark = None
        self.running = True
        self.queries = []                                         

        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Obsługa sygnałów do graceful shutdown"""
        logger.info(f"Otrzymano sygnał {signum}. Zatrzymywanie analizatora...")
        self.running = False

    def _send_to_dashboard(self, endpoint, data):
        """Wysyła dane do dashboard"""
        try:
            response = requests.post(
                f"{self.dashboard_url}/api/{endpoint}",
                json=data,
                timeout=5
            )
            if response.status_code == 200:
                logger.debug(f"Wysłano dane do dashboard: {endpoint}")
            else:
                logger.warning(f"Błąd wysyłania do dashboard: {response.status_code}")
        except Exception as e:
            logger.debug(f"Nie można połączyć z dashboard: {e}")                                

    def _create_spark_session(self):
        """Tworzy sesję Spark"""
        try:
            self.spark = SparkSession.builder\
                .appName("OrderAnalysis")\
                .master(self.spark_master)\
                .config("spark.sql.adaptive.enabled", "false")\
                .config("spark.sql.adaptive.coalescePartitions.enabled", "false")\
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")\
                .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")\
                .config("spark.sql.execution.arrow.pyspark.enabled", "false")\
                .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint")\
                .config("spark.executor.heartbeatInterval", "60s")\
                .config("spark.network.timeout", "300s")\
                .config("spark.rpc.askTimeout", "300s")\
                .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")\
                .getOrCreate()

            self.spark.sparkContext.setLogLevel("WARN")
            logger.info(f"Utworzono sesję Spark: {self.spark_master}")

            os.makedirs("/tmp/spark-checkpoint", exist_ok=True)

        except Exception as e:
            logger.error(f"Błąd tworzenia sesji Spark: {e}")
            raise

    def _define_schema(self):
        """Definiuje schemat danych zamówienia - Definiuje strukturę JSON-a który otrzymujemy z Kafka, żeby Spark wiedział jak parsować dane."""
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
                df = self.spark\
                    .readStream\
                    .format("kafka")\
                    .option("kafka.bootstrap.servers", self.kafka_servers)\
                    .option("subscribe", self.kafka_topic)\
                    .option("startingOffsets", "latest")\
                    .option("failOnDataLoss", "false")\
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
        """Parsuje dane zamówień z JSON - konwertuje surowy strumień z Kafka do struktury DataFrame z odpowiednimi kolumnami."""
        schema = self._define_schema()                                                

        orders_df = kafka_df\
            .select(from_json(col("value").cast("string"), schema).alias("order"))\
            .select("order.*")\
            .withColumn("timestamp_parsed", to_timestamp(col("timestamp")))\
            .withColumn("total_value", col("price") * col("quantity"))

        return orders_df

    def _analyze_top_products(self, orders_df):
        """Analizuje top produkty - agregacja globalna bez okien czasowych"""

        global_analysis = orders_df\
            .groupBy(
                col("product_id"),
                col("product_name"),
                col("category")
            )\
            .agg(                                                
                count("order_id").alias("order_count"),
                sum("quantity").alias("total_quantity"),
                sum("total_value").alias("total_revenue"),
                avg("price").alias("avg_price"),
                max("timestamp_parsed").alias("last_order_time")
            )

        return global_analysis

    def _analyze_categories(self, orders_df):
        """Analizuje sprzedaż po kategoriach - agregacja globalna"""

        category_analysis = orders_df\
            .groupBy(col("category"))\
            .agg(
                count("order_id").alias("order_count"),
                sum("quantity").alias("total_quantity"),
                sum("total_value").alias("total_revenue"),
                approx_count_distinct("product_id").alias("unique_products"),
                max("timestamp_parsed").alias("last_order_time")
            )

        return category_analysis


    def _output_top_products(self, analysis_df):
        """Wyprowadza wyniki analizy produktów"""

        def process_batch(batch_df, batch_id):
            if batch_df.count() > 0:
                logger.info(f"\n{'='*80}")
                logger.info(f"TOP PRODUKTY - Batch {batch_id}")
                logger.info(f"{'='*80}")

                top_products = batch_df\
                    .orderBy(desc("order_count"), desc("total_revenue"))\
                    .limit(10)

                products_list = top_products.collect()

                dashboard_data = []
                for row in products_list:
                    dashboard_data.append({
                        'product_id': row['product_id'],
                        'product_name': row['product_name'],
                        'category': row['category'],
                        'order_count': row['order_count'],
                        'total_quantity': row['total_quantity'],
                        'total_revenue': float(row['total_revenue']),
                        'avg_price': float(row['avg_price']),
                        'window_start': row['last_order_time'].isoformat()
                    })

                self._send_to_dashboard('top_products', {
                    'batch_id': batch_id,
                    'timestamp': datetime.now().isoformat(),
                    'products': dashboard_data
                })

                for i, row in enumerate(products_list, 1):
                    logger.info(f"{i:2d}. {row['product_name']}")
                    logger.info(f"    Kategoria: {row['category']}")
                    logger.info(f"    Zamówienia: {row['order_count']}, Ilość: {row['total_quantity']}")
                    logger.info(f"    Przychód: ${row['total_revenue']:.2f}, Śr. cena: ${row['avg_price']:.2f}")
                    logger.info(f"    Ostatnie zamówienie: {row['last_order_time']}")
                    logger.info("")

        query = analysis_df.writeStream\
            .foreachBatch(process_batch)\
            .outputMode("complete")\
            .trigger(processingTime=f'{self.top_products_interval} seconds')\
            .start()

        return query

    def _output_categories(self, analysis_df):
        """Wyprowadza wyniki analizy kategorii"""

        def process_batch(batch_df, batch_id):
            if batch_df.count() > 0:
                logger.info(f"\n{'='*80}")
                logger.info(f"ANALIZA KATEGORII - Batch {batch_id}")
                logger.info(f"{'='*80}")

                categories = batch_df\
                    .orderBy(desc("total_revenue"))\
                    .collect()

                dashboard_data = []
                for row in categories:
                    dashboard_data.append({
                        'category': row['category'],
                        'order_count': row['order_count'],
                        'total_quantity': row['total_quantity'],
                        'total_revenue': float(row['total_revenue']),
                        'unique_products': row['unique_products'],
                        'last_order_time': row['last_order_time'].isoformat()
                    })

                self._send_to_dashboard('categories', {
                    'batch_id': batch_id,
                    'timestamp': datetime.now().isoformat(),
                    'categories': dashboard_data
                })

                for row in categories:
                    logger.info(f"Kategoria: {row['category']}")
                    logger.info(f"  Zamówienia: {row['order_count']}, Produkty: {row['unique_products']}")
                    logger.info(f"  Przychód: ${row['total_revenue']:.2f}")
                    logger.info(f"  Ostatnie zamówienie: {row['last_order_time']}")
                    logger.info("")

        query = analysis_df.writeStream\
            .foreachBatch(process_batch)\
            .outputMode("complete")\
            .trigger(processingTime=f'{self.categories_interval} seconds')\
            .start()

        return query


    def _output_customer_segments(self, analysis_df):
        """Output customer segment analysis"""
        def process_batch(batch_df, batch_id):
            if batch_df.count() > 0:
                segments = batch_df.collect()

                dashboard_data = []
                for row in segments:
                    dashboard_data.append({
                        'segment': row['customer_segment'],
                        'order_count': row['order_count'],
                        'total_revenue': float(row['total_revenue']),
                        'avg_order_value': float(row['avg_order_value']),
                        'unique_customers': row['unique_customers'],
                        'window_start': row['window_start'].isoformat(),
                        'window_end': row['window_end'].isoformat()
                    })

                self._send_to_dashboard('customer_segments', {
                    'batch_id': batch_id,
                    'timestamp': datetime.now().isoformat(),
                    'segments': dashboard_data
                })

                logger.info(f"Customer Segments Analysis - Batch {batch_id}")
                for row in segments:
                    logger.info(f"  {row['customer_segment']}: {row['order_count']} orders, "
                              f"${row['total_revenue']:.2f} revenue, "
                              f"${row['avg_order_value']:.2f} AOV")

        query = analysis_df.writeStream\
            .foreachBatch(process_batch)\
            .outputMode("append")\
            .trigger(processingTime='20 seconds')\
            .start()

        return query


    def _output_promotions_analysis(self, analysis_df):
        """Output promotions effectiveness analysis"""
        def process_batch(batch_df, batch_id):
            if batch_df.count() > 0:
                promos = batch_df.collect()

                dashboard_data = []
                for row in promos:
                    dashboard_data.append({
                        'promotion_applied': row['promotion_applied'],
                        'order_count': row['order_count'],
                        'total_revenue': float(row['total_revenue']),
                        'avg_order_value': float(row['avg_order_value']),
                        'window_start': row['window_start'].isoformat(),
                        'window_end': row['window_end'].isoformat()
                    })

                self._send_to_dashboard('promotions', {
                    'batch_id': batch_id,
                    'timestamp': datetime.now().isoformat(),
                    'promotions': dashboard_data
                })

                logger.info(f"Promotions Analysis - Batch {batch_id}")
                for row in promos:
                    promo_text = "WITH promotions" if row['promotion_applied'] else "WITHOUT promotions"
                    logger.info(f"  {promo_text}: {row['order_count']} orders, "
                              f"${row['avg_order_value']:.2f} AOV")

        query = analysis_df.writeStream\
            .foreachBatch(process_batch)\
            .outputMode("append")\
            .trigger(processingTime='25 seconds')\
            .start()

        return query


    def _output_raw_orders(self, orders_df):
        """Wyprowadza surowe zamówienia do dashboard"""

        def process_batch(batch_df, batch_id):
            if batch_df.count() > 0:
                recent_orders = batch_df\
                    .orderBy(desc("timestamp_parsed"))\
                    .limit(50)\
                    .collect()

                dashboard_data = []
                for row in recent_orders:
                    dashboard_data.append({
                        'order_id': row['order_id'],
                        'product_id': row['product_id'],
                        'product_name': row['product_name'],
                        'category': row['category'],
                        'price': float(row['price']),
                        'quantity': row['quantity'],
                        'total_value': float(row['total_value']),
                        'customer_id': row['customer_id'],
                        'timestamp': row['timestamp_parsed'].isoformat() if row['timestamp_parsed'] else row['timestamp']
                    })

                self._send_to_dashboard('raw_orders', {
                    'batch_id': batch_id,
                    'timestamp': datetime.now().isoformat(),
                    'orders': dashboard_data
                })

        query = orders_df.writeStream\
            .foreachBatch(process_batch)\
            .outputMode("append")\
            .trigger(processingTime=f'{self.raw_orders_interval} seconds')\
            .start()

        return query


    def run(self):
        """Główna metoda uruchamiająca analizę"""
        logger.info("Rozpoczynanie analizy zamówień...")

        self._create_spark_session()

        kafka_df = self._read_kafka_stream()

        orders_df = self._parse_orders(kafka_df)

        product_analysis = self._analyze_top_products(orders_df)
        category_analysis = self._analyze_categories(orders_df)

        raw_orders_query = self._output_raw_orders(orders_df)
        product_query = self._output_top_products(product_analysis)
        category_query = self._output_categories(category_analysis)


        self.queries = [raw_orders_query, product_query, category_query]

        try:
            while self.running and any(q.isActive for q in self.queries):
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Zatrzymywanie analizy...")
            self.running = False

        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania: {e}")
            self.running = False

        finally:
            self._safe_shutdown(*self.queries)
            self._cleanup_spark()

    def _safe_shutdown(self, *queries):
        """Bezpieczne zatrzymanie zapytań"""
        for query in queries:
            try:
                if query and query.isActive:
                    query.stop()
                    logger.info("Zatrzymano zapytanie strumieniowe")
            except Exception as e:
                logger.warning(f"Błąd podczas zatrzymywania zapytania: {e}")

    def _cleanup_spark(self):
        """Bezpieczne zamykanie sesji Spark"""
        try:
            if self.spark:
                streams = self.spark.streams.active
                for stream in streams:
                    try:
                        stream.stop()
                    except:
                        pass

                self.spark.stop()
                logger.info("Zamknięto sesję Spark")

                time.sleep(2)

        except Exception as e:
            logger.warning(f"Błąd podczas zamykania Spark: {e}")
        finally:
            self.spark = None

def main():
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