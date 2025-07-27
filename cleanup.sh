#!/bin/bash

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "🧹 Czyszczenie systemu Online Store Order Analysis"
echo "=================================================="

# Sprawdź czy system działa
if pgrep -f "QuorumPeerMain\|kafka\.Kafka\|order_simulator\|data_analyzer" > /dev/null; then
    log_warning "System nadal działa. Najpierw zatrzymaj go używając ./stop.sh"
    exit 1
fi

# Usuń logi
if [ -d "logs" ]; then
    log_info "Czyszczenie logów..."
    rm -f logs/*.log
    log_success "Logi wyczyszczone"
fi

# Usuń pliki PID
if [ -d "pids" ]; then
    log_info "Czyszczenie plików PID..."
    rm -f pids/*.pid
    log_success "Pliki PID wyczyszczone"
fi

# Usuń tymczasowe katalogi Spark
log_info "Czyszczenie tymczasowych plików Spark..."
rm -rf /tmp/spark-checkpoint* /tmp/temporary-* 2>/dev/null || true
log_success "Tymczasowe pliki Spark wyczyszczone"

# Usuń dane Zookeeper
log_info "Czyszczenie danych Zookeeper..."
rm -rf /tmp/zookeeper* 2>/dev/null || true
log_success "Dane Zookeeper wyczyszczone"

# Usuń logi Kafka
if [ -d "kafka_2.13-3.9.0/logs" ]; then
    log_info "Czyszczenie logów Kafka..."
    rm -rf kafka_2.13-3.9.0/logs/*
    log_success "Logi Kafka wyczyszczone"
fi

echo ""
log_success "System wyczyszczony! Możesz teraz uruchomić ./start.sh"
