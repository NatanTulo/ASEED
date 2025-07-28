# ASEED - Apache Spark + Kafka E-commerce Analytics

🎯 **System analizy zamówień e-commerce w czasie rzeczywistym**

System symuluje sklep internetowy wysyłający zamówienia przez Kafka, a Spark analizuje które produkty są najpopularniejsze.

## 🚀 Użycie

### 1. Instalacja (jednorazowa)
```bash
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED
./install.sh
```

### 2. Uruchamianie systemu
```bash
# Uruchom wszystko jedną komendą
python3 aseed.py start

# Dashboard dostępny na: http://localhost:5005
```

### 3. Zatrzymywanie
```bash
python3 aseed.py stop
```

### 4. Status systemu
```bash
python3 aseed.py status
```

### 5. Test z danymi (opcjonalnie)
```bash
# Generuj dane przez 5 minut, 20 zamówień/min
python3 aseed.py test --minutes 5 --rate 20
```

## 📊 Co system robi?

- **Order Simulator** → generuje realistyczne zamówienia e-commerce
- **Kafka** → przesyła zamówienia w czasie rzeczywistym
- **Spark** → analizuje które produkty są top sellers
- **Dashboard** → pokazuje wyniki na wykresach

## 🔧 Architektura

```
📱 Simulator → 📡 Kafka → ⚡ Spark → 📊 Dashboard
```

### Komponenty:
- **Zookeeper** + **Kafka** - infrastruktura messaging
- **Order Simulator** - generator zamówień JSON
- **Data Analyzer** - Spark Structured Streaming
- **Web Dashboard** - Flask + Chart.js + WebSocket

## 📁 Struktura plików

```
ASEED/
├── aseed.py                     # 🎯 GŁÓWNY SKRYPT - uruchamiaj tutaj!
├── src/
│   ├── order_simulator.py          # Generator zamówień podstawowy
│   ├── enhanced_order_simulator.py # Generator zaawansowany (promocje, trendy)
│   ├── data_analyzer.py            # Spark analytics + zaawansowane funkcje
│   ├── web_dashboard.py            # Dashboard Flask + WebSocket
│   ├── test_data_generator.py      # Generator danych testowych
│   └── templates/dashboard.html    # Interfejs web (real-time)
├── analysis_demo.ipynb         # 📓 Notebook demonstracyjny
├── test_aseed.py              # 🧪 Testy jednostkowe
├── TECHNICAL_DOCS.md          # 📋 Dokumentacja techniczna
├── logs/                      # Logi wszystkich serwisów
├── pids/                      # PIDs procesów
└── install.sh                # Instalacja zależności
```

## 🛠️ Dodatkowe komendy

### Monitoring
```bash
# Logi w czasie rzeczywistym
tail -f logs/*.log

# Status procesów
ps aux | grep -E "kafka|python"
```

### API Endpoints
- `http://localhost:5005` - Dashboard
- `http://localhost:5005/api/analytics` - JSON z metrykami
- `http://localhost:5005/api/top-products` - Top sellers

### Dodatkowe funkcje
- **Enhanced Simulator**: Promocje, sezonowość, segmenty klientów
- **Zaawansowane analizy**: Trendy godzinowe, skuteczność promocji
- **Jupyter Notebook**: Demonstracja konceptów (`analysis_demo.ipynb`)
- **Testy jednostkowe**: Walidacja funkcji (`python3 test_aseed.py`)
- **Dokumentacja techniczna**: Pełna architektura (`TECHNICAL_DOCS.md`)

## 🐛 Problemy?

1. **Port zajęty**: `pkill -f kafka` i spróbuj ponownie
2. **Brak Javy**: `sudo apt install openjdk-11-jdk`
3. **Brak Python**: Zainstaluj Python 3.8+
4. **Logi**: Sprawdź `logs/` dla szczegółów błędów

## 📈 Dane wyjściowe

System zgodny z wymaganiami:
- **Kafka topic**: zamówienia (order_id, product_id, price, timestamp)
- **Spark Streaming**: aggregacje w czasie rzeczywistym  
- **Top products**: ranking najpopularniejszych produktów
- **ETL patterns**: Kafka → Spark → Dashboard

---

**Jeden skrypt, jeden dashboard, wszystko działa! 🎉**
