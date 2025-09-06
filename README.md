# ASEED - Apache Spark + Kafka E-commerce Analytics

**System analizy zamówień e-commerce w czasie rzeczywistym z Docker**

System symuluje sklep internetowy wysyłający zamówienia przez Kafka, a Spark analizuje które produkty są najpopularniejsze. **Całość działa w kontenerach Docker** dla łatwego wdrożenia.

## 🚀 Użycie z Docker

### 1. Wymagania
- Docker 20.10+ 
- Docker Compose v2+
- 4GB RAM wolnego
- Porty: 5005, 8080, 9092, 2181

### 2. Instalacja i uruchomienie
```bash
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED

# Jednorazowa instalacja i konfiguracja
./docker-aseed.sh install

# Uruchom cały system
./docker-aseed.sh start
```

### 3. Dostęp do systemu
- **📊 Dashboard**: http://localhost:5005
- **⚡ Spark UI**: http://localhost:8080  
- **📊 Kafka**: localhost:9092

### 4. Zarządzanie systemem
```bash
# Status kontenerów
./docker-aseed.sh status

# Logi systemu
./docker-aseed.sh logs

# Logi konkretnego serwisu
./docker-aseed.sh logs web-dashboard

# Restart systemu
./docker-aseed.sh restart

# Zatrzymanie
./docker-aseed.sh stop

# Test z danymi
./docker-aseed.sh test 5 20  # 5 minut, 20 zamówień/min

# Czyszczenie (usuń kontenery i obrazy)
./docker-aseed.sh cleanup
```

## 🐳 Architektura kontenerowa

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   Zookeeper     │──▶│     Kafka       │──▶│  Order Simulator│
│   Container     │   │   Container     │   │    Container    │
└─────────────────┘   └─────────────────┘   └─────────────────┘
                              │
                              ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Spark Master   │──▶│ Data Analyzer   │──▶│  Web Dashboard  │
│   Container     │   │   Container     │   │    Container    │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

### Komponenty kontenerowe:
- **aseed-zookeeper**: Koordynacja Kafka
- **aseed-kafka**: Message broker 
- **aseed-spark-master**: Spark cluster manager
- **aseed-order-simulator**: Generator zamówień (Enhanced)
- **aseed-data-analyzer**: Spark Structured Streaming
- **aseed-web-dashboard**: Flask dashboard z WebSocket

## 📁 Struktura plików

```
ASEED/
├── docker-compose.yml           # 🐳 Definicja kontenerów
├── docker-aseed.sh             # Skrypt zarządzający
├── Dockerfile.python           # Python apps (simulator, dashboard)
├── Dockerfile.spark            # Spark master
├── Dockerfile.spark-app        # Spark applications
├── src/
│   ├── order_simulator.py          # Generator zamówień podstawowy  
│   ├── enhanced_order_simulator.py # Generator zaawansowany (UŻYWANY)
│   ├── data_analyzer.py            # Spark analytics
│   ├── web_dashboard.py            # Dashboard Flask + WebSocket
│   ├── test_data_generator.py      # Generator danych testowych
│   └── templates/dashboard.html    # Interfejs web
├── analysis_demo.ipynb         # 📓 Notebook demonstracyjny
├── test_aseed.py              # 🧪 Testy jednostkowe  
├── TECHNICAL_DOCS_DOCKER.md   # 📋 Dokumentacja Docker
├── requirements.txt           # Python dependencies
└── requirements_dev.txt       # Development dependencies
```

## 🛠️ Dodatkowe komendy Docker

### Monitoring
```bash
# Logi w czasie rzeczywistym
./docker-aseed.sh logs

# Status wszystkich kontenerów
docker ps

# Użycie zasobów
docker stats
```

### Debugging
```bash
# Wejście do kontenera
docker exec -it aseed-web-dashboard /bin/bash

# Restart konkretnego serwisu
./docker-aseed.sh restart-service kafka

# Sprawdzenie sieci
docker network ls | grep aseed
```

### API Endpoints
- `http://localhost:5005` - Dashboard
- `http://localhost:5005/api/analytics` - JSON z metrykami
- `http://localhost:5005/api/top-products` - Top sellers
- `http://localhost:8080` - Spark Master UI

## 📊 Co system robi?

- **Order Simulator** → generuje realistyczne zamówienia e-commerce
- **Kafka** → przesyła zamówienia w czasie rzeczywistym
- **Spark** → analizuje które produkty są top sellers
- **Dashboard** → pokazuje wyniki na wykresach w czasie rzeczywistym

## 🧪 Testowanie

```bash
# Test generowania danych (3 zamówienia co 15 sekund)
docker exec -it aseed-order-simulator python3 test_generator.py 3 15

# Testy jednostkowe
docker exec -it aseed-order-simulator python3 test_aseed.py
```

## 🐛 Problemy?

1. **Port zajęty**: `docker compose down` i spróbuj ponownie
2. **Brak pamięci**: Zwiększ pamięć w Docker Desktop (min 4GB)  
3. **Brak Docker**: Zainstaluj Docker Desktop
4. **Logi błędów**: `docker compose logs [service-name]`
5. **Restart systemu**: `docker compose restart`

## 📈 Dane wyjściowe

System zgodny z wymaganiami:
- **Kafka topic**: zamówienia (order_id, product_id, price, timestamp)
- **Spark Streaming**: agregacje w czasie rzeczywistym  
- **Top products**: ranking najpopularniejszych produktów
- **ETL patterns**: Kafka → Spark → Dashboard
- **Containerization**: Wszystkie komponenty w Docker

---

**System działa w kontenerach Docker.**
