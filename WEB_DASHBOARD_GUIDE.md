# 🌐 Web Dashboard - Kompletny przewodnik

## 📋 **Podsumowanie funkcjonalności**

Web Dashboard to nowoczesny interfejs webowy do zarządzania projektem ASEED - Online Store Order Analysis. Pozwala na pełne zarządzanie systemem bez potrzeby używania terminala.

---

## 🚀 **Szybki start**

```bash
# 1. Zainstaluj projekt (jeśli jeszcze nie masz)
./install.sh

# 2. Uruchom Web Dashboard
./start-dashboard.sh

# 3. Otwórz w przeglądarce
http://localhost:5000
```

---

## 🎯 **Główne funkcjonalności**

### **1. 📊 Monitorowanie w czasie rzeczywistym**

#### **Metryki systemowe (odświeżane co 5 sekund):**
- **CPU Usage** - wykorzystanie procesora z progress barem
- **RAM Usage** - wykorzystanie pamięci z progress barem  
- **Disk Usage** - wykorzystanie dysku z progress barem
- **Load Average** - średnie obciążenie systemu (1min/5min/15min)

#### **Status serwisów:**
- **Zookeeper** - koordynator Kafka
- **Kafka** - broker wiadomości
- **Order Simulator** - generator zamówień
- **Data Analyzer** - analizator Spark

**Dla każdego serwisu widoczne są:**
- Status (🟢 running / 🔴 stopped / 🟡 error)
- PID procesu
- Uptime (czas działania)
- Użycie CPU (%)
- Użycie RAM (MB)

### **2. 🔧 Zarządzanie serwisami**

#### **Dostępne akcje:**
- **Start All** - uruchom wszystkie komponenty jednocześnie
- **Stop All** - zatrzymaj wszystkie komponenty
- **Refresh** - odśwież status wszystkich serwisów

### **3. 📝 Logi w czasie rzeczywistym**

#### **Dostępne logi:**
- **Analyzer** - wyniki analiz, top produkty, statystyki
- **Simulator** - generowane zamówienia, błędy połączenia  
- **Kafka** - działanie brokera wiadomości
- **Zookeeper** - koordynacja klastra

#### **Funkcjonalności:**
- Auto-refresh co 10 sekund
- Auto-scroll do najnowszych wpisów
- Przełączanie między serwisami zakładkami
- Wyświetlanie ostatnich 100 linii

### **4. ⚙️ Konfiguracja systemu**

#### **Edytowalne parametry:**
- **Kafka Bootstrap Servers** - adres serwera Kafka (domyślnie: localhost:9092)
- **Kafka Topic** - nazwa topiku (domyślnie: orders)
- **Orders Per Second** - ile zamówień na sekundę generować (0.1-100)
- **Product Count** - liczba różnych produktów (10-1000)
- **Spark Master URL** - tryb działania Spark (domyślnie: local[*])

#### **Jak to działa:**
1. Zmiany są zapisywane do pliku `.env`
2. Konfiguracja jest walidowana po stronie serwera
3. Restart serwisów wymagany do zastosowania zmian
4. Toast notification potwierdza zapis

### **5. 💻 Komendy systemowe**

#### **Dostępne komendy:**
- **Sprawdź Wymagania** - weryfikuje Java, Python, RAM, dysk
- **Zainstaluj Zależności** - pobiera i instaluje Kafka, Spark, pakiety Python

#### **Wyniki w modalu:**
- Kolorowy output (stdout/stderr)
- Status wykonania (sukces/błąd)
- Returncode procesu
- Timeout dla długo trwających operacji

---

## 🛠️ **Architektura techniczna**

### **Backend (Python Flask):**
```
src/web_dashboard.py
├── SystemMonitor class
│   ├── get_system_status()      # Status serwisów + metryki
│   ├── get_recent_logs()        # Ostatnie logi serwisu  
│   ├── get_configuration()      # Aktualny config z .env
│   ├── update_configuration()   # Zapis nowego configu
│   └── execute_command()        # Wykonanie komendy systemowej
├── Flask routes
│   ├── / (dashboard)            # Główna strona
│   ├── /api/status             # Status JSON API
│   ├── /api/logs/<service>     # Logi JSON API
│   ├── /api/config            # Config GET/POST API
│   └── /api/command/<cmd>      # Wykonanie komendy API
└── WebSocket handlers
    ├── status_update           # Real-time updates
    └── background_updater      # Wątek w tle
```

### **Frontend (HTML + JavaScript):**
```
src/templates/dashboard.html
├── Bootstrap 5 UI
│   ├── Responsive grid system
│   ├── Cards dla metryk/serwisów
│   ├── Progress bars
│   ├── Modals dla komend
│   └── Forms dla konfiguracji
├── Socket.IO client
│   ├── Real-time status updates
│   ├── Auto-reconnection
│   └── Event handling
└── Vanilla JavaScript
    ├── API calls (fetch)
    ├── DOM manipulation
    ├── Form validation
    └── Auto-refresh logiki
```

---

## 🔌 **API Endpoints**

### **GET /api/status**
Zwraca pełny status systemu w JSON:
```json
{
  "timestamp": "2024-01-15 14:30:25",
  "zookeeper": {
    "status": "running",
    "pid": 12345,
    "uptime": "2h 15m",
    "cpu_percent": 2.1,
    "memory_mb": 145.8
  },
  "kafka": { ... },
  "order_simulator": { ... },
  "data_analyzer": { ... },
  "system_resources": {
    "cpu_percent": 15.4,
    "memory_percent": 68.2,
    "disk_percent": 45.1,
    "load_average": [0.85, 0.72, 0.69]
  }
}
```

### **GET /api/logs/{service_name}?lines=100**
Zwraca ostatnie logi dla serwisu:
```json
{
  "logs": [
    "2024-01-15 14:30:25 - INFO - Analiza zakończona",
    "2024-01-15 14:30:20 - INFO - Przetwarzanie batch 156",
    ...
  ]
}
```

### **GET /api/config**
Zwraca aktualną konfigurację:
```json
{
  "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
  "KAFKA_TOPIC": "orders",
  "ORDERS_PER_SECOND": "2",
  "PRODUCT_COUNT": "50",
  "SPARK_MASTER_URL": "local[*]"
}
```

### **POST /api/config**
Zapisuje nową konfigurację:
```json
// Request body
{
  "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
  "ORDERS_PER_SECOND": "5",
  "PRODUCT_COUNT": "100"
}

// Response
{
  "success": true
}
```

### **POST /api/command/{command}**
Wykonuje komendę systemową:
```json
// Response
{
  "success": true,
  "returncode": 0,
  "stdout": "System started successfully...",
  "stderr": "",
  "message": null
}
```

---

## 🌐 **WebSocket Events**

### **Client → Server:**
- `connect` - nawiązanie połączenia
- `request_status` - żądanie aktualnego statusu

### **Server → Client:**
- `status` - pełny status systemu (przy połączeniu)
- `status_update` - aktualizacje co 5 sekund

---

## 📁 **Struktura plików**

```
ASEED/
├── src/
│   ├── web_dashboard.py        # Główna aplikacja Flask
│   └── templates/
│       └── dashboard.html      # Interfejs HTML
├── start-dashboard.sh          # Skrypt uruchamiający
├── dashboard-utils.sh          # Funkcje pomocnicze
├── WEB_DASHBOARD.md           # Ta dokumentacja
└── logs/                      # Logi serwisów (monitorowane)
    ├── data_analyzer.log
    ├── order_simulator.log
    ├── kafka.log
    └── zookeeper.log
```

---

## ⚡ **Performance & Skalowalność**

### **Wydajność:**
- WebSocket updates co 5 sekund (konfigurowalne)
- Log refresh co 10 sekund (konfigurowalne)
- Asynchroniczny background updater
- Caching statusu procesu (psutil)

### **Limits:**
- Timeout komend: 30-600 sekund
- Max logi: 100 linii na serwis
- Max output: 60KB (auto-truncation)
- Concurrent connections: unlimited

### **Memory Usage:**
- Flask app: ~50-100MB RAM
- Real-time monitoring: ~10-20MB RAM
- WebSocket overhead: ~5MB per connection

---

## 🐛 **Troubleshooting**

### **Dashboard nie startuje:**
```bash
# Sprawdź czy pakiety są zainstalowane
source venv/bin/activate
pip install flask flask-socketio psutil

# Sprawdź czy port 5000 jest wolny
netstat -tlnp | grep :5000

# Uruchom debug mode
cd src
python web_dashboard.py
```

### **Serwisy pokazują błędny status:**
```bash
# Sprawdź czy katalogi istnieją
ls -la logs/ pids/

# Sprawdź uprawnienia
chmod 755 logs/ pids/

# Ręcznie sprawdź procesy
ps aux | grep -E "(kafka|spark|python)"
```

### **Konfiguracja się nie zapisuje:**
```bash
# Sprawdź uprawnienia do pliku .env
ls -la .env
chmod 644 .env

# Sprawdź zawartość
cat .env
```

### **Logi nie ładują się:**
```bash
# Sprawdź czy pliki logów istnieją
ls -la logs/

# Sprawdź uprawnienia
chmod 644 logs/*.log

# Sprawdź ostatnie wpisy
tail logs/data_analyzer.log
```

---

## 🎨 **Customization**

### **Zmiana portu:**
```python
# W pliku src/web_dashboard.py na końcu:
socketio.run(app, host='0.0.0.0', port=8080, debug=False)
```

### **Zmiana częstotliwości updateów:**
```python
# W funkcji background_status_updater():
time.sleep(10)  # Zmień z 5 na 10 sekund
```

### **Dodanie nowych metryk:**
```python
# W metodzie _get_system_resources():
return {
    'cpu_percent': psutil.cpu_percent(interval=1),
    'memory_percent': psutil.virtual_memory().percent,
    'disk_percent': psutil.disk_usage('/').percent,
    'network_io': psutil.net_io_counters(),  # NOWA METRYKA
    'load_average': os.getloadavg()
}
```

### **Dodanie nowych serwisów:**
```python
# W metodzie get_system_status():
status = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'zookeeper': self._check_process_status('zookeeper'),
    'kafka': self._check_process_status('kafka'),
    'order_simulator': self._check_process_status('order_simulator'),
    'data_analyzer': self._check_process_status('data_analyzer'),
    'web_server': self._check_process_status('web_server'),  # NOWY SERWIS
    'system_resources': self._get_system_resources()
}
```

---

## 💡 **Best Practices**

### **Bezpieczeństwo:**
- Dashboard działa lokalnie (localhost:5000)
- Brak uwierzytelniania (internal tool)
- Walidacja komend po stronie serwera
- Timeout dla operacji systemowych

### **Monitoring:**
- Regularnie sprawdzaj logi dashboard w terminalu
- Monitor resource usage (htop/top)
- Backup konfiguracji przed zmianami

### **Development:**
- Użyj debug mode do developmentu
- Test API endpoints przez curl/Postman
- Sprawdź browser console w razie problemów

---

## 🚀 **Future Enhancements**

### **Planowane funkcjonalności:**
- **Wykresy w czasie rzeczywistym** (Chart.js już załadowany)
- **Historia metryk** z zapisem do bazy  
- **Email/SMS alerting** dla krytycznych błędów
- **Export/Import** konfiguracji
- **Multi-instance** monitoring (wiele projektów)
- **REST API** dla integracji z innymi narzędziami
- **Docker integration** dla konteneryzacji
- **Authentication** dla produkcyjnego użycia

Web Dashboard znacznie ułatwia zarządzanie projektem ASEED i jest idealny zarówno do prezentacji jak i codziennego użytku! 🎉
