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

show_menu() {
    echo "📊 Monitoring Online Store Order Analysis"
    echo "========================================="
    echo ""
    echo "Wybierz co chcesz monitorować:"
    echo ""
    echo "1) Logi analizatora danych (wyniki analiz)"
    echo "2) Logi symulatora zamówień"
    echo "3) Logi Kafka"
    echo "4) Logi Zookeeper"
    echo "5) Status wszystkich procesów"
    echo "6) Wszystkie logi na żywo"
    echo "7) Wyjście"
    echo ""
    echo -n "Wybór [1-7]: "
}

monitor_data_analyzer() {
    log_info "Monitorowanie analizatora danych (Ctrl+C aby wrócić do menu)"
    echo "================================================================"
    if [ -f "logs/data_analyzer.log" ]; then
        tail -f logs/data_analyzer.log
    else
        echo "Plik logs/data_analyzer.log nie istnieje"
        echo "Czy analizator jest uruchomiony? Sprawdź: ./start.sh"
    fi
}

monitor_order_simulator() {
    log_info "Monitorowanie symulatora zamówień (Ctrl+C aby wrócić do menu)"
    echo "=============================================================="
    if [ -f "logs/order_simulator.log" ]; then
        tail -f logs/order_simulator.log
    else
        echo "Plik logs/order_simulator.log nie istnieje"
        echo "Czy symulator jest uruchomiony? Sprawdź: ./start.sh"
    fi
}

monitor_kafka() {
    log_info "Monitorowanie Kafka (Ctrl+C aby wrócić do menu)"
    echo "==============================================="
    if [ -f "logs/kafka.log" ]; then
        tail -f logs/kafka.log
    else
        echo "Plik logs/kafka.log nie istnieje"
        echo "Czy Kafka jest uruchomiona? Sprawdź: ./start.sh"
    fi
}

monitor_zookeeper() {
    log_info "Monitorowanie Zookeeper (Ctrl+C aby wrócić do menu)"
    echo "=================================================="
    if [ -f "logs/zookeeper.log" ]; then
        tail -f logs/zookeeper.log
    else
        echo "Plik logs/zookeeper.log nie istnieje"
        echo "Czy Zookeeper jest uruchomiony? Sprawdź: ./start.sh"
    fi
}

show_process_status() {
    log_info "Status procesów systemu"
    echo "======================="
    echo ""
    
    # Sprawdź Zookeeper
    if pgrep -f "kafka.zookeeper" > /dev/null; then
        ZK_PID=$(pgrep -f "kafka.zookeeper")
        log_success "Zookeeper: DZIAŁA (PID: $ZK_PID)"
    else
        echo -e "${RED}❌ Zookeeper: NIE DZIAŁA${NC}"
    fi
    
    # Sprawdź Kafka
    if pgrep -f "kafka.Kafka" > /dev/null; then
        KAFKA_PID=$(pgrep -f "kafka.Kafka")
        log_success "Kafka: DZIAŁA (PID: $KAFKA_PID)"
    else
        echo -e "${RED}❌ Kafka: NIE DZIAŁA${NC}"
    fi
    
    # Sprawdź Order Simulator
    if pgrep -f "order_simulator.py" > /dev/null; then
        SIM_PID=$(pgrep -f "order_simulator.py")
        log_success "Order Simulator: DZIAŁA (PID: $SIM_PID)"
    else
        echo -e "${RED}❌ Order Simulator: NIE DZIAŁA${NC}"
    fi
    
    # Sprawdź Data Analyzer
    if pgrep -f "data_analyzer.py" > /dev/null; then
        ANA_PID=$(pgrep -f "data_analyzer.py")
        log_success "Data Analyzer: DZIAŁA (PID: $ANA_PID)"
    else
        echo -e "${RED}❌ Data Analyzer: NIE DZIAŁA${NC}"
    fi
    
    echo ""
    
    # Sprawdź porty
    log_info "Status portów:"
    if netstat -ln 2>/dev/null | grep -q ":2181"; then
        log_success "Port 2181 (Zookeeper): OTWARTY"
    else
        echo -e "${RED}❌ Port 2181 (Zookeeper): ZAMKNIĘTY${NC}"
    fi
    
    if netstat -ln 2>/dev/null | grep -q ":9092"; then
        log_success "Port 9092 (Kafka): OTWARTY"
    else
        echo -e "${RED}❌ Port 9092 (Kafka): ZAMKNIĘTY${NC}"
    fi
    
    echo ""
    echo -n "Naciśnij Enter aby wrócić do menu..."
    read
}

monitor_all_logs() {
    log_info "Monitorowanie wszystkich logów (Ctrl+C aby wrócić do menu)"
    echo "=========================================================="
    
    # Sprawdź które pliki logów istnieją
    log_files=""
    
    if [ -f "logs/data_analyzer.log" ]; then
        log_files="$log_files logs/data_analyzer.log"
    fi
    
    if [ -f "logs/order_simulator.log" ]; then
        log_files="$log_files logs/order_simulator.log"
    fi
    
    if [ -f "logs/kafka.log" ]; then
        log_files="$log_files logs/kafka.log"
    fi
    
    if [ -f "logs/zookeeper.log" ]; then
        log_files="$log_files logs/zookeeper.log"
    fi
    
    if [ -n "$log_files" ]; then
        tail -f $log_files
    else
        echo "Brak plików logów do monitorowania"
        echo "Czy system jest uruchomiony? Sprawdź: ./start.sh"
        echo ""
        echo -n "Naciśnij Enter aby wrócić do menu..."
        read
    fi
}

main() {
    while true; do
        clear
        show_menu
        read choice
        
        case $choice in
            1)
                clear
                monitor_data_analyzer
                ;;
            2)
                clear
                monitor_order_simulator
                ;;
            3)
                clear
                monitor_kafka
                ;;
            4)
                clear
                monitor_zookeeper
                ;;
            5)
                clear
                show_process_status
                ;;
            6)
                clear
                monitor_all_logs
                ;;
            7)
                echo ""
                log_info "Do widzenia!"
                exit 0
                ;;
            *)
                echo ""
                echo -e "${RED}Nieprawidłowy wybór. Spróbuj ponownie.${NC}"
                sleep 2
                ;;
        esac
    done
}

main "$@"
