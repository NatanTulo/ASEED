# Online Store Order A![Dashboard Preview](docs/dashboard-preview.png)

## 🧪 Generator danych testowych

Do testowania wizualizacji dostępny jest generator przykładowych zamówień:

```bash
# Generuj dane przez 2 minuty (6 zamówień/min)
./generate-test-data.sh

# Lub z custom parametrami
./generate-test-data.sh 5 10  # 5 minut, 10 zamówień/min
```

## 🏗️ Architekturaysis

Projekt symulujący sklep internetowy wysyłający dane o zamówieniach przez Kafka, które są następnie analizowane przez Apache Spark w celu identyfikacji najlepiej sprzedających się produktów.

## � Web Dashboard

Projekt zawiera nowoczesny **interfejs webowy** do zarządzania i monitorowania systemu:

```bash
./start-dashboard.sh
# Otwórz: http://localhost:5000
```

### Funkcjonalności Dashboard:
- **📊 Monitorowanie w czasie rzeczywistym** - CPU, RAM, Dysk, Load Average
- **🔧 Zarządzanie serwisami** - Start/Stop wszystkich komponentów jednym kliknięciem  
- **📝 Podgląd logów** - Real-time logi dla każdego serwisu
- **⚙️ Konfiguracja** - Edycja wszystkich parametrów przez GUI
- **💻 Komendy systemowe** - Instalacja, sprawdzenie wymagań przez interfejs
- **📈 Wizualizacje danych** - Wykresy zamówień, top produkty, trendy kategorii
- **🧪 Generator danych testowych** - Symulacja ruchu dla testów dashboard

![Dashboard Preview](docs/dashboard-preview.png)

## �🏗️ Architektura

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

### Metoda 1: Web Dashboard (NOWA - ZALECANE!)
```bash
# Pobierz projekt
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED

# Zainstaluj zależności
./install.sh

# Uruchom Web Dashboard
./start-dashboard.sh
```
**Następnie otwórz:** http://localhost:5000

### Metoda 2: Interaktywne demo
```bash
# Pobierz projekt
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED

# Uruchom interaktywny przewodnik
./demo.sh
```

### Metoda 3: Automatyczna instalacja (jedna komenda)
```bash
# Pobierz projekt
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED

# Automatyczna instalacja + uruchomienie
./quickstart.sh
```

## 🎯 Demo i testowanie

### 🌐 Web Dashboard z wizualizacjami (NOWOŚĆ!):
```bash
# Kompletna demonstracja z interaktywnymi wykresami
./demo-full.sh
```
**Funkcje dashboardu:**
- 📊 **Real-time analytics** - zamówienia i przychody na żywo
- 📈 **Wykresy trendów** - sprzedaż w czasie (Chart.js)
- 🥧 **Wykres kategorii** - podział produktów (doughnut chart)
- 🏆 **TOP 10 produktów** - ranking najpopularniejszych
- 🖥️ **System monitoring** - CPU, RAM, disk
- 🎛️ **Sterowanie systemem** - start/stop usług z poziomu web

### Szybkie demo (konsola):
```bash
./demo.sh
```

### Krok po kroku:
```bash
# 1. Uruchom wszystkie usługi
./start.sh

# 2. Opcja A: Web Dashboard (zalecane)
./start-dashboard.sh       # Dostępny: http://localhost:5000

# 2. Opcja B: Generuj przykładowe zamówienia (konsola)
python3 src/order_simulator.py

# 3. W innym terminalu - analizuj dane
python3 src/data_analyzer.py
```

### Dane testowe dla wizualizacji:
```bash
# Podstawowe (2 min, 6 zamówień/min)
./generate-test-data.sh

# Intensywne (5 min, 20 zamówień/min)  
./generate-test-data.sh 5 20

# Długie (10 min, 2 zamówienia/min)
./generate-test-data.sh 10 2
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
