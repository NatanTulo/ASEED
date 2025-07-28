#!/bin/bash

# 🚀 ASEED - Kompletna demonstracja z wizualizacjami
# Uruchamia system symulacji zamówień + Web Dashboard z wykresami

echo "🚀 ASEED - Uruchamianie kompletnej demonstracji z wizualizacjami"
echo "================================================================"

# Sprawdź czy jest zainstalowane
if [ ! -f ".setup_complete" ]; then
    echo "❌ System nie jest zainstalowany. Uruchom najpierw:"
    echo "   ./install.sh"
    exit 1
fi

# Sprawdź czy komponenty działają
echo "🔍 Sprawdzanie komponentów..."

if ! pgrep -f kafka > /dev/null; then
    echo "⚠️ Kafka nie działa. Uruchamianie..."
    ./start.sh
    sleep 5
fi

# Generuj dane testowe w tle
echo "📊 Generowanie danych testowych dla wizualizacji..."
./generate-test-data.sh 10 8 &  # 10 minut, 8 zamówień/min
DATA_PID=$!

# Uruchom analizę danych w tle 
echo "🔬 Uruchamianie analizy danych..."
nohup python3 src/data_analyzer.py > logs/demo_analyzer.log 2>&1 &
ANALYZER_PID=$!

# Czekaj chwilę na wygenerowanie pierwszych danych
echo "⏳ Czekanie na pierwsze dane (30 sekund)..."
sleep 30

# Uruchom Web Dashboard
echo "🌐 Uruchamianie Web Dashboard z wizualizacjami..."
echo "   Dostępny pod adresem: http://localhost:5000"
echo ""
echo "📈 Funkcje wizualizacji:"
echo "   • Real-time analytics (zamówienia, przychody)"
echo "   • Wykres trendów sprzedaży (ostatnie 12h)"  
echo "   • Wykres kategorii produktów (doughnut chart)"
echo "   • Ranking TOP 10 najpopularniejszych produktów"
echo "   • System monitoring (CPU, RAM, Disk)"
echo "   • Live log streaming w konsoli"
echo ""
echo "🛠️ Sterowanie systemem:"
echo "   • Start/Stop usług Kafka/Spark"
echo "   • Generowanie danych testowych"
echo "   • Zarządzanie procesami w czasie rzeczywistym"
echo ""
echo "🎯 Demo będzie działać przez 10 minut z automatyczną generacją danych"
echo "   Naciśnij Ctrl+C aby zatrzymać"
echo ""

# Zapisz PID-y procesów
echo $DATA_PID > pids/demo_data.pid
echo $ANALYZER_PID > pids/demo_analyzer.pid

# Funkcja cleanup przy wyjściu
cleanup() {
    echo ""
    echo "🛑 Zatrzymywanie demonstracji..."
    
    # Zatrzymaj generator danych testowych
    if [ -f pids/demo_data.pid ]; then
        kill $(cat pids/demo_data.pid) 2>/dev/null
        rm -f pids/demo_data.pid
    fi
    
    # Zatrzymaj analyzer
    if [ -f pids/demo_analyzer.pid ]; then
        kill $(cat pids/demo_analyzer.pid) 2>/dev/null
        rm -f pids/demo_analyzer.pid
    fi
    
    echo "✅ Demonstracja zakończona"
    echo "💡 Komponenty Kafka/Spark pozostają uruchomione"
    echo "   Użyj './stop.sh' aby je zatrzymać"
    exit 0
}

# Przechwytuj sygnał przerwania
trap cleanup INT TERM

# Uruchom Web Dashboard (blokująco)
./start-dashboard.sh

# Jeśli dashboard się zakończył, wywołaj cleanup
cleanup
