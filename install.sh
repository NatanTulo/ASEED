#!/bin/bash
# ASEED - Instalator systemu

set -e

echo "🎯 ASEED - Instalacja systemu analizy zamówień"
echo "============================================="

# Sprawdź czy Java jest zainstalowana
if ! command -v java &> /dev/null; then
    echo "❌ Java nie jest zainstalowana"
    echo "Zainstaluj: sudo apt-get update && sudo apt-get install openjdk-11-jdk"
    exit 1
fi

echo "✅ Java: $(java -version 2>&1 | head -n 1)"

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nie jest zainstalowany"
    echo "Zainstaluj: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

echo "✅ Python: $(python3 --version)"

# Stwórz środowisko wirtualne
if [ ! -d "venv" ]; then
    echo "🔧 Tworzenie środowiska wirtualnego..."
    python3 -m venv venv
fi

# Aktywuj środowisko
source venv/bin/activate

# Zainstaluj zależności Python
echo "📦 Instalacja zależności Python..."
pip install -r requirements.txt

# Pobierz Kafka jeśli nie istnieje
if [ ! -d "kafka_2.13-3.9.0" ]; then
    echo "📡 Pobieranie Apache Kafka..."
    if [ ! -f "kafka_2.13-3.9.0.tgz" ]; then
        wget -q https://downloads.apache.org/kafka/3.9.0/kafka_2.13-3.9.0.tgz
    fi
    tar -xzf kafka_2.13-3.9.0.tgz
    rm -f kafka_2.13-3.9.0.tgz
fi

# Pobierz Spark jeśli nie istnieje
if [ ! -d "spark-3.5.6-bin-hadoop3" ]; then
    echo "⚡ Pobieranie Apache Spark..."
    if [ ! -f "spark-3.5.6-bin-hadoop3.tgz" ]; then
        wget -q https://downloads.apache.org/spark/spark-3.5.6/spark-3.5.6-bin-hadoop3.tgz
    fi
    tar -xzf spark-3.5.6-bin-hadoop3.tgz
    rm -f spark-3.5.6-bin-hadoop3.tgz
fi

# Stwórz katalogi
mkdir -p logs pids

echo ""
echo "✅ 🎉 Instalacja zakończona pomyślnie!"
echo ""
echo "🚀 Uruchom system: python3 aseed.py start"
echo "📊 Dashboard: http://localhost:5005"
echo "🛑 Zatrzymaj: python3 aseed.py stop"
