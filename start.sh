#!/bin/bash

set -e

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

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Załaduj zmienne środowiskowe z pliku .env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    log_info "Załadowano konfigurację z .env"
fi

# Sprawdź czy katalogi Kafka i Spark istnieją
check_installation() {
    KAFKA_DIR="kafka_2.13-3.9.0"
    SPARK_DIR="spark-3.5.0-bin-hadoop3"
    
    if [ ! -d "$KAFKA_DIR" ]; then
        log_error "Kafka nie jest zainstalowana w katalogu $KAFKA_DIR. Uruchom najpierw ./install.sh"
        exit 1
    fi
    
    if [ ! -d "$SPARK_DIR" ]; then
        log_error "Spark nie jest zainstalowana w katalogu $SPARK_DIR. Uruchom najpierw ./install.sh"
        exit 1
    fi
    
    if [ ! -d "venv" ]; then
        log_error "Wirtualne środowisko Python nie istnieje. Uruchom najpierw ./install.sh"
        exit 1
    fi
}

# Uruchom Zookeeper
start_zookeeper() {
    log_info "Uruchamianie Zookeeper..."
    
    # Sprawdź czy Zookeeper już działa
    if pgrep -f "QuorumPeerMain" > /dev/null; then
        log_warning "Zookeeper już działa"
        return
    fi
    
    cd $KAFKA_DIR
    nohup bin/zookeeper-server-start.sh ./config/zookeeper.properties > ../logs/zookeeper.log 2>&1 &
    ZOOKEEPER_PID=$!
    echo $ZOOKEEPER_PID > ../pids/zookeeper.pid
    cd ..
    
    # Czekaj na uruchomienie - sprawdzaj przez 30 sekund
    log_info "Czekam na uruchomienie Zookeeper..."
    for i in {1..30}; do
        if pgrep -f "QuorumPeerMain" > /dev/null; then
            log_success "Zookeeper uruchomiony (PID: $(pgrep -f 'QuorumPeerMain'))"
            return
        fi
        sleep 1
    done
    
    log_error "Nie udało się uruchomić Zookeeper po 30 sekundach"
    log_error "Sprawdź logi: tail -f logs/zookeeper.log"
    exit 1
}

# Uruchom Kafka
start_kafka() {
    log_info "Uruchamianie Kafka..."
    
    # Sprawdź czy Kafka już działa
    if pgrep -f "kafka.Kafka" > /dev/null; then
        log_warning "Kafka już działa"
        return
    fi
    
    cd $KAFKA_DIR
    nohup bin/kafka-server-start.sh config/server.properties > ../logs/kafka.log 2>&1 &
    KAFKA_PID=$!
    echo $KAFKA_PID > ../pids/kafka.pid
    cd ..
    
    # Czekaj na uruchomienie - sprawdzaj przez 60 sekund
    log_info "Czekam na uruchomienie Kafka..."
    for i in {1..60}; do
        if pgrep -f "kafka.Kafka" > /dev/null; then
            log_success "Kafka uruchomiona (PID: $(pgrep -f 'kafka.Kafka'))"
            return
        fi
        sleep 1
    done
    
    log_error "Nie udało się uruchomić Kafka po 60 sekundach"
    log_error "Sprawdź logi: tail -f logs/kafka.log"
    exit 1
}

# Utwórz topic Kafka
create_kafka_topic() {
    log_info "Tworzenie topiku Kafka 'orders'..."
    
    # Czekaj dodatkowo 5 sekund na pełne uruchomienie Kafka
    log_info "Czekam na pełną gotowość Kafka..."
    sleep 5
    
    cd $KAFKA_DIR
    
    # Sprawdź czy topic już istnieje
    if bin/kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null | grep -q "^orders$"; then
        log_warning "Topic 'orders' już istnieje"
    else
        # Próbuj utworzyć topic z retry
        local retries=3
        local success=false
        
        for i in $(seq 1 $retries); do
            log_info "Próba utworzenia topiku (${i}/${retries})..."
            if bin/kafka-topics.sh --create \
                --bootstrap-server localhost:9092 \
                --replication-factor 1 \
                --partitions 3 \
                --topic orders 2>/dev/null; then
                success=true
                break
            else
                log_info "Próba ${i} nieudana, czekam 3 sekundy..."
                sleep 3
            fi
        done
        
        if [ "$success" = true ]; then
            log_success "Topic 'orders' utworzony"
        else
            log_error "Nie udało się utworzyć topiku po $retries próbach"
            exit 1
        fi
    fi
    
    cd ..
}

# Uruchom Order Simulator
start_order_simulator() {
    log_info "Uruchamianie symulatora zamówień..."
    
    # Sprawdź czy symulator już działa
    if pgrep -f "order_simulator.py" > /dev/null; then
        log_warning "Symulator zamówień już działa"
        return
    fi
    
    source venv/bin/activate
    nohup python src/order_simulator.py > logs/order_simulator.log 2>&1 &
    SIMULATOR_PID=$!
    echo $SIMULATOR_PID > pids/order_simulator.pid
    
    log_success "Symulator zamówień uruchomiony (PID: $SIMULATOR_PID)"
}

# Uruchom Data Analyzer
start_data_analyzer() {
    log_info "Uruchamianie analizatora danych..."
    
    # Sprawdź czy analizator już działa
    if pgrep -f "data_analyzer.py" > /dev/null; then
        log_warning "Analizator danych już działa"
        return
    fi
    
    source venv/bin/activate
    nohup python src/data_analyzer.py > logs/data_analyzer.log 2>&1 &
    ANALYZER_PID=$!
    echo $ANALYZER_PID > pids/data_analyzer.pid
    
    log_success "Analizator danych uruchomiony (PID: $ANALYZER_PID)"
}

# Utwórz katalogi dla logów i PID
create_directories() {
    mkdir -p logs
    mkdir -p pids
}

# Główna funkcja
main() {
    echo "🚀 Uruchamianie Online Store Order Analysis"
    echo "==========================================="
    echo ""
    
    check_installation
    
    # Ustaw nazwy katalogów
    KAFKA_DIR="kafka_2.13-3.9.0"
    SPARK_DIR="spark-3.5.0-bin-hadoop3"
    
    create_directories
    
    start_zookeeper
    start_kafka
    create_kafka_topic
    start_order_simulator
    start_data_analyzer
    
    echo ""
    log_success "🎉 System uruchomiony pomyślnie!"
    echo ""
    log_info "Aby monitorować system:"
    log_info "  ./monitor.sh - obejrzyj logi w czasie rzeczywistym"
    echo ""
    log_info "Aby zatrzymać system:"
    log_info "  ./stop.sh - zatrzymaj wszystkie serwisy"
    echo ""
    log_warning "System potrzebuje kilku minut na pełne uruchomienie"
    log_warning "Sprawdź logi za 2-3 minuty: tail -f logs/data_analyzer.log"
}

main "$@"
