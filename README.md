# ASEED - Apache Spark + Kafka E-commerce Analytics

🎯 **System analizy zamówień e-commerce w czasie rzeczywistym**

System symuluje realistyczny sklep internetowy wysyłający zamówienia przez Kafka, a Spark analizuje które produkty są najpopularniejsze na podstawie ilości sprzedanych sztuk.

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

### 5. Restart systemu
```bash
python3 aseed.py restart
```

### 6. Test z danymi (opcjonalnie)
```bash
# Generuj dane przez 5 minut, 20 zamówień/min
python3 aseed.py test --minutes 5 --rate 20
```

## 📊 Co system robi?

- **Order Simulator** → generuje realistyczne zamówienia z konkretnymi cenami
- **Kafka** → przesyła zamówienia w losowych odstępach (3-8 sekund)
- **Spark** → analizuje produkty według **sprzedanych sztuk** (nie tylko zamówień)
- **Dashboard** → wykresy w czasie rzeczywistym z pełnymi nazwami produktów

## 🛍️ Realistyczne produkty i ceny

System zawiera **60 produktów** w 6 kategoriach z **konkretnymi cenami**:

### Electronics ($25-650):
- Smart LED TV: $649.99
- Digital Camera: $449.99  
- Smart Watch: $299.99
- Gaming Mechanical Keyboard: $129.99
- Wireless Bluetooth Headphones: $79.99
- Smartphone Case: $24.99

### Clothing ($20-160):
- Leather Boots: $159.99
- Winter Jacket: $149.99
- Running Sneakers: $119.99
- Cotton T-Shirt: $19.99

### Books ($13-50):
- History Encyclopedia: $49.99
- Programming Guide: $39.99
- Mystery Novel: $14.99
- Poetry Collection: $12.99

### Home ($20-180):
- Coffee Maker: $179.99
- Kitchen Knife Set: $89.99
- Bed Sheets: $54.99
- Picture Frame: $19.99

### Sports ($19-200):
- Fitness Tracker: $199.99
- Dumbbells Set: $149.99
- Tennis Racket: $89.99
- Water Bottle: $18.99

### Beauty ($8-80):
- Perfume: $79.99
- Makeup Brush Set: $49.99
- Face Moisturizer: $32.99
- Lip Balm: $7.99

## 📈 Dashboard Features

### Wykresy:
- **Top Products** - ranking według **sprzedanych sztuk** (nie zamówień)
- **Categories** - wykres kołowy według zamówień z szczegółowymi tooltipami
- **Real-time Orders** - ostatnie 10 zamówień na żywo

### Tooltips w wykresach:
Po najechaniu na kategorię zobaczysz:
- Liczba zamówień
- Sprzedane sztuki  
- Przychody
- Unikalne produkty

### Nazwy produktów:
- Długie nazwy dzielą się na kilka linijek
- Pełne nazwy bez skrótów typu "..."

## 🔧 Architektura

```
📱 Simulator → 📡 Kafka → ⚡ Spark → 📊 Dashboard
   (3-8s)      (stream)   (analyze)   (real-time)
```

### Komponenty:
- **Zookeeper** + **Kafka** - infrastruktura messaging
- **Order Simulator** - generator realistycznych zamówień
- **Data Analyzer** - Spark agregacja globalnych statystyk
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

## 🎯 Kluczowe usprawnienia

### Realistyczne zamówienia:
- **Losowe interwały**: 3-8 sekund między zamówieniami
- **Stałe ceny**: każdy produkt ma swoją konkretną cenę
- **Sensowne nazwy**: "Wireless Bluetooth Headphones" zamiast losowych słów

### Inteligentne analizy:
- **Sprzedane sztuki**: wykres pokazuje łączną liczbę sprzedanych produktów
- **Globalna agregacja**: wszystkie zamówienia od uruchomienia systemu
- **Bez duplikatów**: każdy produkt pojawia się raz w rankingu

### Ulepszone UI:
- **Wieloliniowe etykiety**: długie nazwy dzielą się na linijki
- **Zaawansowane tooltips**: pełne informacje o kategoriach
- **Status monitoringu**: real-time status wszystkich serwisów

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
