# 📊 Wizualizacje danych w Web Dashboard

## 🎯 Przegląd funkcjonalności

Web Dashboard ASEED oferuje **kompletne wizualizacje danych w czasie rzeczywistym**, które przekształcają surowe logi w interaktywne wykresy i statystyki.

---

## 🌟 **Kluczowe wizualizacje**

### **1. 📈 Sekcja analityczna (Real-time)**
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Analiza Zamówień w Czasie Rzeczywistym                 │
├─────────────────────────────────────────────────────────────┤
│  [15] Zamówienia/min  [$847.55] Przychód/min              │
│  [$56.50] Śr. wartość [$12,450] Łączne zamówienia         │
└─────────────────────────────────────────────────────────────┘
```

### **2. 📊 Wykres trendów zamówień (Ostatnie 12h)**
- **Linia zamówień** - liczba zamówień w czasie
- **Linia przychodów** - przychody w dolarach
- **Dual Y-axis** - różne skale dla lepszej czytelności
- **Real-time updates** - odświeżanie co 5 sekund

### **3. 🥧 Wykres kategorii produktów**
- **Doughnut chart** - podział według kategorii
- **Kolorowe segmenty** - łatwa identyfikacja
- **Legendy** - nazwy kategorii z wartościami

### **4. 🏆 Top 10 produktów**
```
🥇 Electronics Smart Watch 15    [45 szt.] [$2,847.55]
🥈 Clothing Fashion Jacket       [38 szt.] [$1,923.42]  
🥉 Books Python Programming      [32 szt.] [$1,471.68]
4. Home Coffee Machine           [28 szt.] [$1,599.72]
...
```

---

## 🔍 **Jak działa parsowanie danych**

### **Źródła danych:**
1. **order_simulator.log** - surowe zamówienia JSON
2. **data_analyzer.log** - wyniki analiz Spark
3. **System metrics** - CPU, RAM, disk z psutil

### **Pipeline przetwarzania:**
```
Raw Logs → Parser → DataAnalyzer → Agregacja → WebSocket → Charts
```

### **Przykład parsowania zamówienia:**
```python
# Z loga: "2024-01-15 14:30:25 - order_simulator - INFO - Wysłano zamówienie: {...}"
order_data = {
    'order_id': 'ORD-123456',
    'product_name': 'Electronics Smart Watch 15',
    'category': 'Electronics', 
    'price': 299.99,
    'quantity': 2,
    'timestamp': '2024-01-15T14:30:25'
}
```

---

## 📊 **Metryki w czasie rzeczywistym**

### **Obliczane automatycznie:**
- **Orders/minute** - zamówienia z ostatniej minuty
- **Revenue/minute** - przychód z ostatniej minuty  
- **Average order value** - średnia wartość zamówienia
- **Total orders** - suma wszystkich zamówień
- **Total products** - liczba unikalnych produktów
- **Total categories** - liczba kategorii

### **Agregacje:**
- **Produkty** - ranking według liczby sprzedanych sztuk
- **Kategorie** - podział według typu produktu
- **Trendy godzinowe** - okna czasowe 1h

---

## 🛠️ **Technologie wizualizacji**

### **Chart.js - główna biblioteka wykresów:**
```javascript
// Wykres trendów zamówień
ordersChart = new Chart(ctx, {
    type: 'line',
    data: {
        datasets: [
            { label: 'Zamówienia', borderColor: 'rgb(75, 192, 192)' },
            { label: 'Przychód ($)', borderColor: 'rgb(255, 99, 132)' }
        ]
    }
});

// Wykres kategorii  
categoryChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', ...]
    }
});
```

### **WebSocket real-time updates:**
```javascript
socket.on('analytics_update', function(data) {
    updateAnalytics(data);      // Metryki
    updateOrdersChart(data);    // Wykres trendów
    updateCategoryChart(data);  // Wykres kategorii
    updateTopProducts(data);    // Ranking produktów
});
```

---

## 🧪 **Generator danych testowych**

### **Uruchomienie:**
```bash
# Podstawowe (2 min, 6 zamówień/min)
./generate-test-data.sh

# Intensywne (5 min, 20 zamówień/min) 
./generate-test-data.sh 5 20

# Długie (10 min, 2 zamówienia/min)
./generate-test-data.sh 10 2
```

### **Co generuje:**
- **Realistyczne produkty** - 10 kategorii (Electronics, Clothing, Books, etc.)
- **Zmienne ceny** - od $5.99 do $299.99  
- **Różne ilości** - 1-5 sztuk na zamówienie
- **Timestamps** - chronologiczne znaczniki czasu
- **JSON format** - kompatybilny z parserem

### **Przykład wygenerowanego zamówienia:**
```json
{
  "order_id": "ORD-456789",
  "product_id": "PROD-001", 
  "product_name": "Electronics Smart Watch 15",
  "category": "Electronics",
  "price": 299.99,
  "quantity": 1,
  "customer_id": "CUST-5678",
  "timestamp": "2024-01-15T14:30:25.123456"
}
```

---

## 📈 **Możliwości analityczne**

### **1. Analiza sprzedaży:**
- Które produkty sprzedają się najlepiej?
- Jakie kategorie generują największy przychód?
- Kiedy występują szczyty sprzedaży?

### **2. Trendy czasowe:**
- Wzorce godzinowe/dzienne
- Sezonowość sprzedaży
- Prognozy na podstawie historii

### **3. Segmentacja produktów:**
- Top/middle/long tail products
- Produkty o wysokiej marży
- Bestsellery vs produkty niszowe

---

## 🎨 **Personalizacja wizualizacji**

### **Kolory wykresów:**
```css
/* Gradient background dla sekcji analitycznej */
.analytics-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Kolorowe progress bary */
.progress-bar.bg-primary { background: #007bff; }
.progress-bar.bg-info { background: #17a2b8; }
.progress-bar.bg-warning { background: #ffc107; }
```

### **Responsywność:**
- **Desktop** - pełne dashboardy z wszystkimi wykresami
- **Tablet** - stackowane sekcje, mniejsze wykresy  
- **Mobile** - kompaktowy widok, główne metryki

---

## 🔧 **Konfiguracja zaawansowana**

### **Częstotliwość aktualizacji:**
```python
# W web_dashboard.py
time.sleep(5)  # Status updates co 5 sekund
```

```javascript  
// W dashboard.html
setInterval(() => {
    loadAnalytics();
}, 5000);  // Analityka co 5 sekund
```

### **Limity danych:**
```python
class DataAnalyzer:
    def __init__(self):
        self.order_history = deque(maxlen=1000)      # Ostatnie 1000 zamówień
        self.recent_metrics = deque(maxlen=60)       # 5 minut przy update co 5s
```

### **Parsowanie logów:**
```python
# Regex patterns dla różnych formatów logów
order_pattern = r'Wysłano zamówienie: ({.*})'
product_pattern = r'(\d+)\.\s+(.+?)\s+Sprzedane:\s*(\d+)'
revenue_pattern = r'Przychód:\s*\$?([\d,]+\.?\d*)'
```

---

## 🚀 **Rozszerzenia przyszłościowe**

### **Planowane funkcjonalności:**
1. **Alerting** - powiadomienia przy anomaliach
2. **Export danych** - CSV/Excel z wykresów  
3. **Filtering** - filtrowanie według daty/kategorii
4. **Zoom & Pan** - interakcja z wykresami
5. **Historical data** - dane historyczne z bazy
6. **Multi-tenancy** - wiele sklepów jednocześnie

### **Integracje:**
- **Elasticsearch** - przeszukiwanie logów
- **InfluxDB** - time series database
- **Grafana** - zaawansowane dashboardy
- **Slack/Email** - notyfikacje

---

## 📋 **Best Practices**

### **Wydajność:**
1. **Limit danych** - nie ładuj więcej niż potrzeba
2. **Debouncing** - unikaj zbyt częstych updateów
3. **Lazy loading** - ładuj wykresy na żądanie
4. **Caching** - cache heavy computations

### **UX/UI:**
1. **Loading states** - spinners podczas ładowania
2. **Error handling** - graceful degradation  
3. **Tooltips** - dodatkowe informacje na hover
4. **Color accessibility** - kolory dla daltonistów

### **Dane:**
1. **Data validation** - sprawdzaj poprawność danych
2. **Fallback values** - domyślne wartości przy błędach
3. **Time zones** - obsługa stref czasowych
4. **Data retention** - polityka przechowywania danych

---

**Dashboard ASEED z wizualizacjami przekształca surowe logi Big Data w interaktywne, zrozumiałe wykresy które pomagają w analizie biznesowej i technicznej!** 📊✨
