# Online Store Order Analysis

Projekt symulujący sklep internetowy wysyłający dane o zamówieniach przez Kafka, które są następnie analizowane przez Apache Spark w celu identyfikacji najlepiej sprzedających się produktów.

## 🏗️ Architektura

- **Apache Kafka + Zookeeper**: System kolejek wiadomości do strumieniowego przesyłania zamówień
- **Apache Spark**: Silnik do analizy strumieniowej danych w trybie lokalnym
- **Order Simulator**: Generator symulowanych zamówień (Python + Kafka Producer)
- **Data Analyzer**: Analizator real-time z metrykami top produktów (PySpark Structured Streaming)

## 📋 Wymagania

- **4GB RAM** (minimum)
- **2GB wolnego miejsca na dysku**
- **Internet** (do pobierania Apache Kafka i Spark)

**Automatycznie instalowane:**
- **Java 11+**
- **Python 3** z pip
- **Apache Kafka 3.9.0**
- **Apache Spark 3.5.0**
- **Wymagane biblioteki Python** (pyspark, kafka-python, faker)

## 🚀 Szybki start

### Metoda 1: Interaktywne demo (ZALECANE dla nowych użytkowników)
```bash
# Pobierz projekt
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED

# Uruchom interaktywny przewodnik
./demo.sh
```

### Metoda 2: Automatyczna instalacja (jedna komenda)
```bash
# Pobierz projekt
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED

# Automatyczna instalacja + uruchomienie
./quickstart.sh
```

## 🚀 Krok po kroku

### 1. Sprawdź wymagania systemu
```bash
./check-requirements.sh
```

### 2. Zainstaluj wszystkie zależności
```bash
./install.sh
```

### 3. Uruchom system
```bash
./start.sh
```

### 4. Monitoruj działanie
```bash
./monitor.sh
```

### 5. Zatrzymaj system
```bash
./stop.sh
```

### Alternatywnie - użyj Makefile
```bash
make check     # sprawdź wymagania
make install   # zainstaluj zależności  
make start     # uruchom system
make monitor   # monitoruj
make stop      # zatrzymaj
```

## 📊 Co zobaczysz

### Logi analizy w czasie rzeczywistym
```bash
# Monitoruj wyniki analizy
./monitor.sh  # wybierz opcję 1

# Lub bezpośrednio:
tail -f logs/data_analyzer.log
```

### Przykładowe wyniki
```
================================================================================
TOP PRODUKTY - Batch 123
================================================================================
 1. Electronics Smart Watch 15
    Kategoria: Electronics
    Zamówienia: 8, Ilość: 15
    Przychód: $1,247.85, Śr. cena: $83.19
    Okno: 2025-01-15 14:30:00 - 2025-01-15 14:31:00

 2. Clothing Designer Jacket 7
    Kategoria: Clothing  
    Zamówienia: 6, Ilość: 12
    Przychód: $987.32, Śr. cena: $164.55
```

### Status systemu
```bash
# Sprawdź czy wszystkie komponenty działają
./monitor.sh  # wybierz opcję 5
```

## ⚙️ Konfiguracja

Edytuj plik `.env` aby dostosować parametry:

```env
# Częstotliwość generowania zamówień
ORDERS_PER_SECOND=2

# Liczba różnych produktów w katalogu
PRODUCT_COUNT=50

# Tryb Spark (local[*] używa wszystkich rdzeni procesora)
SPARK_MASTER_URL=local[*]
```

## 🛠️ Struktura projektu

```
ASEED/
├── src/                          # Kod źródłowy aplikacji
│   ├── order_simulator.py        # Generator zamówień
│   └── data_analyzer.py          # Analizator Spark
├── logs/                         # Logi systemowe (tworzone automatycznie)
├── pids/                         # Pliki PID procesów (tworzone automatycznie)
├── venv/                         # Wirtualne środowisko Python (tworzone automatycznie)
├── kafka_2.13-3.9.0/            # Apache Kafka (pobrane automatycznie)
├── spark-3.5.0-bin-hadoop3/     # Apache Spark (pobrane automatycznie)
├── .env                          # Konfiguracja środowiska
├── requirements.txt              # Pakiety Python
├── install.sh                    # Skrypt instalacji
├── start.sh                      # Skrypt uruchomienia
├── stop.sh                       # Skrypt zatrzymania
├── monitor.sh                    # Skrypt monitorowania
├── check-requirements.sh         # Sprawdzenie wymagań
├── quickstart.sh                 # Szybki start
├── demo.sh                       # Interaktywny przewodnik
├── Makefile                      # Automatyzacja zadań
└── TROUBLESHOOTING.md            # Przewodnik rozwiązywania problemów
```

## 🔧 Dostosowania

### Modyfikacja produktów
Edytuj `src/order_simulator.py`:
- Zmień kategorie w metodzie `_generate_products()`
- Dostosuj popularność produktów w `_generate_product_weights()`

### Dodanie nowych analiz
Edytuj `src/data_analyzer.py`:
- Dodaj nowe agregacje w klasie `OrderAnalyzer`
- Stwórz nowe okna czasowe dla różnych metryk

## 🔧 Troubleshooting

### Najczęstsze problemy:

**1. Błąd "Port already in use"**
```bash
# Sprawdź co używa portów
netstat -tlnp | grep -E ':(2181|9092)'

# Zatrzymaj system i uruchom ponownie
./stop.sh
./start.sh
```

**2. Błąd "Java not found"**
```bash
# Ubuntu/Debian
sudo apt install openjdk-11-jdk

# CentOS/RHEL/Fedora  
sudo dnf install java-11-openjdk-devel
```

**3. Błąd "No space left on device"**
```bash
# Wyczyść stare logi
rm -rf logs/*

# Sprawdź miejsce na dysku
df -h
```

**4. Spark nie może się połączyć z Kafka**
```bash
# Sprawdź czy Kafka działa
./monitor.sh  # opcja 5

# Sprawdź logi
tail -f logs/kafka.log
```

**5. Brak wyników analizy**
```bash
# Sprawdź czy symulator wysyła dane
tail -f logs/order_simulator.log

# Sprawdź topic Kafka
kafka_2.13-3.9.0/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --from-beginning
```

## 🎯 Cele edukacyjne

Ten projekt demonstruje:
- ✅ **Kafka Producers/Consumers** - streaming danych w czasie rzeczywistym
- ✅ **Spark Structured Streaming** - analiza strumieniowa z agregatami okien czasowych  
- ✅ **Lokalne środowisko Big Data** - bez potrzeby klastra lub Docker
- ✅ **ETL Patterns** - extract, transform, load w środowisku strumieniowym
- ✅ **Real-time Analytics** - metryki biznesowe na żywo

## 📈 Rozszerzenia

### Proste rozszerzenia:
- Dodaj więcej kategorii produktów
- Implementuj sezonowość w popularności produktów  
- Dodaj analizę klientów (customer analytics)
- Zapisz wyniki do plików CSV lub JSON

### Zaawansowane rozszerzenia:
- Integracja z bazą danych (PostgreSQL/MySQL)
- Dashboard w Streamlit lub Flask
- Machine Learning dla predykcji trendów
- Integracja z systemami zewnętrznymi przez REST API

## 🧪 Testowanie

```bash
# Sprawdź czy wszystkie komponenty działają
./check-requirements.sh

# Uruchom system na 5 minut i zatrzymaj
./start.sh
sleep 300
./stop.sh
```

---

**💡 Wskazówka**: System używa lokalnego trybu Spark (`local[*]`), więc nie potrzebuje klastra ani Docker. Wszystko działa na jednej maszynie!
