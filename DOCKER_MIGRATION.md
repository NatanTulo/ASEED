# ASEED Docker Migration Guide

## 🐳 Przegląd zmian

System ASEED został zmigrowany do architektury kontenerowej Docker dla łatwiejszego wdrożenia i zarządzania.

## 📦 Nowe pliki

### Docker Configuration
- `docker-compose.yml` - Definicja wszystkich kontenerów i serwisów
- `Dockerfile.python` - Obraz dla aplikacji Python (simulator, dashboard)
- `Dockerfile.spark` - Obraz dla Spark Master
- `Dockerfile.spark-app` - Obraz dla aplikacji Spark (data analyzer)
- `.dockerignore` - Pliki ignorowane podczas budowania obrazów

### Scripts & Documentation
- `docker-aseed.sh` - Skrypt instalacji i zarządzania systemem Docker
- `TECHNICAL_DOCS_DOCKER.md` - Dokumentacja techniczna architektury Docker
- `README.md` - Zaktualizowane README z instrukcjami Docker

### Core Components  
- `src/order_simulator.py` - Generator zamówień e-commerce

## 🔄 Sposób użycia

### Docker (Zalecany)
```bash
# Instalacja i uruchomienie
./docker-aseed.sh install
./docker-aseed.sh start

# Zatrzymanie
./docker-aseed.sh stop
```

### Docker
```bash
# Jednorazowa instalacja
./docker-aseed.sh install

# Uruchomienie
./docker-aseed.sh start

# Zatrzymanie
./docker-aseed.sh stop
```

## 🏗️ Architektura kontenerowa

### Kontenery
1. **aseed-zookeeper** - Koordynacja Kafka
2. **aseed-kafka** - Message broker
3. **aseed-spark-master** - Zarządzanie klastrem Spark  
4. **aseed-order-simulator** - Generator zamówień e-commerce
5. **aseed-data-analyzer** - Aplikacja Spark Streaming
6. **aseed-web-dashboard** - Dashboard Flask z WebSocket

### Sieć
- Dedykowana sieć `aseed-network` (bridge)
- Komunikacja wewnętrzna przez nazwy serwisów
- Publiczne porty tylko dla dostępu zewnętrznego

### Dane
- Logi montowane jako wolumeny
- Kod aplikacji kopiowany do kontenerów
- Brak persistence (dane w pamięci kontenerów)

## 🔧 Konfiguracja

### Environment Variables
Konfiguracja przez zmienne środowiskowe w `docker-compose.yml`:

```yaml
# Order Simulator
KAFKA_BOOTSTRAP_SERVERS: "kafka:29092"
MIN_ORDER_INTERVAL: "3"
MAX_ORDER_INTERVAL: "8"

# Data Analyzer
SPARK_MASTER_URL: "spark://spark-master:7077"

# Dashboard
FLASK_HOST: "0.0.0.0"
FLASK_PORT: "5005"
```

## 📊 Monitoring

### Status kontenerów
```bash
./docker-aseed.sh status
docker ps
```

### Logi
```bash
./docker-aseed.sh logs                # Wszystkie
./docker-aseed.sh logs web-dashboard  # Konkretny serwis
```

### Metryki zasobów
```bash
docker stats
```

## 🧪 Testowanie

### Docker
```bash
./docker-aseed.sh test 5 20  # 5 min, 20 zamówień/min
```

## 🐛 Rozwiązywanie problemów

### Problemy z Docker
```bash
# Sprawdź czy Docker działa
docker --version
docker ps

# Restart systemu
./docker-aseed.sh restart

# Czyszczenie (usuń kontenery i obrazy)
./docker-aseed.sh cleanup

# Sprawdź logi błędów
./docker-aseed.sh logs [service-name]
```

### Port conflicts
```bash
# Sprawdź co używa portów
sudo netstat -tulpn | grep :5005
sudo netstat -tulpn | grep :9092

# Zatrzymaj wszystko i wyczyść
./docker-aseed.sh stop
./docker-aseed.sh cleanup
```

## 📈 Korzyści Docker

### Development
- ✅ Konsystentne środowisko na wszystkich maszynach
- ✅ Brak konfliktów z lokalnymi instalacjami
- ✅ Łatwy restart pojedynczych serwisów
- ✅ Izolacja problemów w kontenerach

### Deployment  
- ✅ Jednolite wdrożenia (dev/staging/prod)
- ✅ Łatwiejsze skalowanie poziome
- ✅ Automatyczne health checks
- ✅ Szybsze uruchamianie (obrazy cache)

### Operations
- ✅ Centralne zarządzanie logami
- ✅ Monitoring zasobów per kontener
- ✅ Łatwe backup/restore
- ✅ Network isolation

## 🔮 Następne kroki

### Możliwe ulepszenia
- [ ] Kubernetes manifests dla produkcji
- [ ] Docker Swarm dla multi-node
- [ ] Prometheus/Grafana monitoring
- [ ] Persistent volumes dla danych Kafka
- [ ] SSL/TLS encryption
- [ ] Auto-scaling based on load
- [ ] CI/CD pipeline z Docker

### Compatibility
- ✅ Wszystkie funkcje zachowane
- ✅ API endpoints niezmienione
- ✅ Dashboard interface identyczny

---

**System został zmigrowny do kontenerów Docker.**
