# Troubleshooting Guide

## 🔧 Najczęstsze problemy i rozwiązania

### 1. Problemy z instalacją

#### Java nie jest zainstalowana
```
❌ Błąd: Java nie jest zainstalowana
```

**Rozwiązanie:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk

# CentOS/RHEL/Fedora
sudo dnf install java-11-openjdk-devel

# macOS (z Homebrew)
brew install openjdk@11
```

#### Python nie jest zainstalowany
```
❌ Błąd: Python 3 nie jest zainstalowany
```

**Rozwiązanie:**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL/Fedora
sudo dnf install python3 python3-pip

# macOS (z Homebrew)
brew install python
```

#### Brak narzędzi systemowych
```
❌ Błąd: wget/curl nie jest zainstalowany
```

**Rozwiązanie:**
```bash
# Ubuntu/Debian
sudo apt install wget curl unzip

# CentOS/RHEL/Fedora
sudo dnf install wget curl unzip

# macOS (z Homebrew)
brew install wget curl
```

### 2. Problemy z portami

#### Port już używany
```
❌ Błąd: Port 9092/2181 jest już używany
```

**Diagnostyka:**
```bash
# Sprawdź co używa portów
netstat -tlnp | grep -E ':(2181|9092)'
lsof -i :9092
lsof -i :2181
```

**Rozwiązanie:**
```bash
# Opcja 1: Zatrzymaj procesy używające portów
sudo pkill -f kafka
sudo pkill -f zookeeper

# Opcja 2: Zmień porty w konfiguracji (zaawansowane)
# Edytuj kafka_2.13-3.9.0/config/server.properties
# Edytuj kafka_2.13-3.9.0/config/zookeeper.properties
```

### 3. Problemy z pamięcią

#### Za mało pamięci RAM
```
❌ Błąd: Za mało pamięci RAM: 2GB (wymagane: 4GB)
```

**Rozwiązanie:**
```bash
# Zmniejsz zużycie pamięci przez Spark
# Edytuj .env:
SPARK_MASTER_URL=local[1]  # Użyj tylko 1 rdzeń

# Lub uruchom z mniejszymi parametrami Spark
export SPARK_DRIVER_MEMORY=512m
export SPARK_EXECUTOR_MEMORY=512m
```

#### System działa wolno
```
⚠️  System działa wolno
```

**Rozwiązanie:**
```bash
# Zmniejsz częstotliwość zamówień
# Edytuj .env:
ORDERS_PER_SECOND=1
PRODUCT_COUNT=20

# Zwiększ okna czasowe w analizie
# Edytuj src/data_analyzer.py - zmień window("1 minute") na window("2 minutes")
```

### 4. Problemy z siecią

#### Brak połączenia internetowego
```
❌ Błąd: Brak połączenia internetowego
```

**Rozwiązanie:**
```bash
# Sprawdź połączenie
curl -I https://www.google.com

# Jeśli jesteś za proxy, skonfiguruj:
export http_proxy=http://proxy:port
export https_proxy=https://proxy:port
```

#### Proxy blokuje pobieranie
```
❌ Błąd: Nie można pobrać Kafka/Spark
```

**Rozwiązanie:**
```bash
# Pobierz ręcznie i rozpakuj w katalogu projektu:
# Kafka: https://downloads.apache.org/kafka/3.9.0/kafka_2.13-3.9.0.tgz
# Spark: https://downloads.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz

wget https://downloads.apache.org/kafka/3.9.0/kafka_2.13-3.9.0.tgz
tar -xzf kafka_2.13-3.9.0.tgz

wget https://downloads.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz  
tar -xzf spark-3.5.0-bin-hadoop3.tgz
```

### 5. Problemy z działaniem systemu

#### Kafka nie uruchamia się
```
❌ Kafka nie działa
```

**Diagnostyka:**
```bash
# Sprawdź logi Kafka
tail -f logs/kafka.log

# Sprawdź logi Zookeeper
tail -f logs/zookeeper.log

# Sprawdź procesy
ps aux | grep kafka
```

**Rozwiązanie:**
```bash
# Wyczyść logi Kafka
rm -rf kafka_2.13-3.9.0/logs/*

# Zrestartuj system
./stop.sh
sleep 5
./start.sh
```

#### Spark không może się połączyć z Kafka
```
❌ Connection refused: localhost:9092
```

**Diagnostyka:**
```bash
# Sprawdź czy Kafka działa
./monitor.sh  # opcja 5

# Sprawdź czy topic istnieje
kafka_2.13-3.9.0/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

**Rozwiązanie:**
```bash
# Utwórz topic ręcznie
kafka_2.13-3.9.0/bin/kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic orders
```

#### Brak danych w analizie
```
ℹ️  Brak wyników analizy
```

**Diagnostyka:**
```bash
# Sprawdź czy symulator wysyła dane
tail -f logs/order_simulator.log

# Sprawdź czy dane docierają do Kafka
kafka_2.13-3.9.0/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --from-beginning
```

**Rozwiązanie:**
```bash
# Restart symulatora
pkill -f order_simulator.py
source venv/bin/activate
nohup python src/order_simulator.py > logs/order_simulator.log 2>&1 &
```

### 6. Problemy z bibliotekami Python

#### Błąd importu pyspark
```
❌ ModuleNotFoundError: No module named 'pyspark'
```

**Rozwiązanie:**
```bash
# Reaktywuj środowisko wirtualne i zainstaluj pakiety
source venv/bin/activate
pip install -r requirements.txt

# Lub zainstaluj ręcznie
pip install pyspark[sql]==3.5.0 kafka-python==2.0.2 faker==19.6.2
```

#### Błąd kompatybilności Java-Spark
```
❌ Unsupported class file major version
```

**Rozwiązanie:**
```bash
# Sprawdź wersję Java
java -version

# Zainstaluj Java 11 (nie nowszą)
sudo apt install openjdk-11-jdk

# Ustaw JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

### 7. Problemy z systemem plików

#### Brak uprawnień
```
❌ Permission denied
```

**Rozwiązanie:**
```bash
# Nadaj uprawnienia skryptom
chmod +x *.sh

# Sprawdź właściciela plików
ls -la

# Zmień właściciela jeśli potrzeba
sudo chown -R $USER:$USER .
```

#### Brak miejsca na dysku
```
❌ No space left on device
```

**Rozwiązanie:**
```bash
# Wyczyść logi
make clean

# Sprawdź miejsce
df -h

# Usuń niepotrzebne pliki
rm -rf kafka_2.13-3.6.0/logs/*
rm -rf /tmp/spark-*
```

## 🔍 Narzędzia diagnostyczne

### Sprawdzenie statusu systemu
```bash
# Kompletna diagnostyka
./monitor.sh  # opcja 5

# Przez Makefile
make status
```

### Monitorowanie logów
```bash
# Wszystkie logi na żywo
./monitor.sh  # opcja 6

# Pojedynczy komponent
tail -f logs/data_analyzer.log
tail -f logs/order_simulator.log
tail -f logs/kafka.log
```

### Testowanie połączeń
```bash
# Test Kafka consumer
kafka_2.13-3.9.0/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic orders

# Test połączenia z Zookeeper
kafka_2.13-3.9.0/bin/kafka-broker-api-versions.sh \
  --bootstrap-server localhost:9092
```

### Sprawdzenie środowiska Python
```bash
# Aktywuj środowisko i sprawdź pakiety
source venv/bin/activate
pip list | grep -E "(pyspark|kafka|faker)"

# Test importów
python -c "import pyspark; print('PySpark OK')"
python -c "import kafka; print('Kafka OK')"
python -c "import faker; print('Faker OK')"
```

## 🚨 W ostateczności - pełny reset

Jeśli nic nie pomaga:

```bash
# 1. Zatrzymaj wszystko
./stop.sh
pkill -f kafka
pkill -f zookeeper
pkill -f python

# 2. Wyczyść wszystko
rm -rf kafka_2.13-3.9.0
rm -rf spark-3.5.0-bin-hadoop3
rm -rf venv
rm -rf logs
rm -rf pids

# 3. Zainstaluj od nowa
./install.sh
./start.sh
```

## 📞 Dalsze wsparcie

Jeśli nadal masz problemy:

1. Sprawdź czy wszystkie wymagania są spełnione: `./check-requirements.sh`
2. Przejrzyj logi: `./monitor.sh`
3. Spróbuj uruchomić krok po kroku zamiast `./quickstart.sh`
4. Sprawdź czy nie ma konfliktów z innymi aplikacjami używającymi portów 2181 i 9092

**Najczęstsze przyczyny problemów:**
- Za mało pamięci RAM (< 4GB)
- Zajęte porty 2181 lub 9092
- Brak połączenia internetowego podczas instalacji
- Niekompatybilne wersje Java (używaj Java 11)
