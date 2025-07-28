# Web Dashboard dla ASEED

## 🌐 Interfejs webowy dla Online Store Order Analysis

Web Dashboard to nowoczesny interfejs webowy, który pozwala na:

### ✨ **Funkcjonalności:**

1. **Monitorowanie w czasie rzeczywistym:**
   - Status wszystkich serwisów (Zookeeper, Kafka, Simulator, Analyzer)
   - Metryki systemowe (CPU, RAM, Dysk, Load Average)
   - Automatyczne odświeżanie co 5 sekund

2. **Zarządzanie serwisami:**
   - Start/Stop wszystkich komponentów
   - Sprawdzanie statusu i PID procesów
   - Informacje o uptime i użyciu zasobów

3. **Podgląd logów:**
   - Logi w czasie rzeczywistym dla każdego serwisu
   - Przełączanie między różnymi logami
   - Automatyczne przewijanie do najnowszych wpisów

4. **Konfiguracja systemu:**
   - Edycja wszystkich parametrów (Kafka, liczba zamówień, produktów)
   - Zapis konfiguracji do pliku .env
   - Walidacja formularzy

5. **Wykonywanie komend systemowych:**
   - Sprawdzenie wymagań systemu
   - Instalacja zależności
   - Wyświetlanie wyników w modalach

### 🚀 **Uruchomienie:**

```bash
# Standardowe uruchomienie
./start-dashboard.sh

# Lub ręcznie
source venv/bin/activate
cd src
python web_dashboard.py
```

### 🌐 **Dostęp:**
- **URL:** http://localhost:5000
- **Port:** 5000
- **WebSocket:** Tak (automatyczne aktualizacje)

### 📱 **Interfejs:**

Dashboard zawiera:

#### **1. Nagłówek z metrykami systemowymi:**
- CPU Usage z progress barem
- RAM Usage z progress barem  
- Disk Usage z progress barem
- Load Average (1min/5min/15min)

#### **2. Panel serwisów:**
- Status każdego komponentu (🟢 running / 🔴 stopped / 🟡 error)
- PID, uptime, CPU i RAM dla każdego procesu
- Przyciski Start All / Stop All / Refresh

#### **3. Panel logów:**
- Zakładki dla każdego serwisu
- Real-time tail logów
- Auto-scroll do najnowszych wpisów
- Odświeżanie co 10 sekund

#### **4. Panel konfiguracji:**
- Kafka Bootstrap Servers
- Kafka Topic
- Orders Per Second (suwak)
- Product Count
- Spark Master URL
- Przycisk "Zapisz Konfigurację"

#### **5. Panel komend systemowych:**
- "Sprawdź Wymagania" 
- "Zainstaluj Zależności"
- Wyniki w modalu z kolorowym outputem

### 🔧 **Technologie:**

**Backend:**
- **Flask** - framework webowy
- **Flask-SocketIO** - WebSocket dla real-time updates
- **psutil** - monitorowanie systemu
- **subprocess** - wykonywanie komend

**Frontend:**
- **Bootstrap 5** - responsywny UI
- **Font Awesome** - ikony
- **Chart.js** - wykresy (gotowe do rozszerzenia)
- **Socket.IO** - komunikacja real-time
- **Vanilla JavaScript** - logika frontendowa

### 📊 **Real-time Features:**

1. **WebSocket connection** - automatyczne aktualizacje
2. **Status updates** co 5 sekund
3. **Log streaming** co 10 sekund
4. **Resource monitoring** w czasie rzeczywistym
5. **Responsive alerts** dla akcji użytkownika

### 🎨 **UI/UX:**

- **Responsywny design** - działa na desktop i mobile
- **Kolorowe statusy** - łatwe rozpoznawanie stanów
- **Progress bary** - wizualizacja wykorzystania zasobów
- **Hover effects** - interaktywne karty
- **Toast notifications** - feedback dla użytkownika
- **Dark theme** dla terminala - professional look

### 🔒 **Bezpieczeństwo:**

- Lokalny dostęp (localhost:5000)
- Brak uwierzytelniania (internal tool)
- Walidacja komend po stronie serwera
- Timeout dla długo trwających operacji

### 📈 **Rozszerzalność:**

Dashboard jest przygotowany do rozszerzenia o:
- Wykresy w czasie rzeczywistym (Chart.js już załadowany)
- Historię metryk
- Alerting i notyfikacje
- Export logów
- Backup/restore konfiguracji

Dashboard znacznie ułatwia zarządzanie projektem ASEED i jest idealny do prezentacji oraz codziennego użytku!
