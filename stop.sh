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

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Zatrzymaj proces na podstawie PID file
stop_process() {
    local service_name=$1
    local pid_file="pids/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Zatrzymywanie $service_name (PID: $pid)..."
            kill "$pid"
            
            # Czekaj na zatrzymanie
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                log_warning "Wymuszenie zatrzymania $service_name..."
                kill -9 "$pid"
            fi
            
            log_success "$service_name zatrzymany"
        else
            log_warning "$service_name nie działa (PID $pid nie istnieje)"
        fi
        rm -f "$pid_file"
    else
        log_warning "Brak pliku PID dla $service_name"
    fi
}

# Zatrzymaj procesy na podstawie nazwy
stop_by_name() {
    local process_name=$1
    local service_name=$2
    
    local pids=$(pgrep -f "$process_name")
    if [ -n "$pids" ]; then
        log_info "Zatrzymywanie $service_name..."
        kill $pids
        sleep 2
        
        # Sprawdź czy nadal działają
        local remaining_pids=$(pgrep -f "$process_name")
        if [ -n "$remaining_pids" ]; then
            log_warning "Wymuszenie zatrzymania $service_name..."
            kill -9 $remaining_pids
        fi
        
        log_success "$service_name zatrzymany"
    else
        log_info "$service_name nie działa"
    fi
}

main() {
    echo "🛑 Zatrzymywanie Online Store Order Analysis"
    echo "============================================"
    echo ""
    
    # Zatrzymaj komponenty aplikacji
    stop_process "data_analyzer"
    stop_process "order_simulator"
    
    # Zatrzymaj Kafka i Zookeeper (także sprawdź według nazwy procesu)
    stop_by_name "kafka.Kafka" "Kafka"
    stop_by_name "kafka.zookeeper" "Zookeeper"
    
    # Dodatkowo zatrzymaj według PID files
    stop_process "kafka"
    stop_process "zookeeper"
    
    echo ""
    log_success "🎉 System zatrzymany"
    
    # Sprawdź czy wszystkie procesy zostały zatrzymane
    echo ""
    log_info "Sprawdzanie pozostałych procesów..."
    
    if pgrep -f "kafka" > /dev/null; then
        log_warning "Niektóre procesy Kafka nadal działają:"
        pgrep -f "kafka" | while read pid; do
            echo "  PID: $pid - $(ps -p $pid -o command --no-headers)"
        done
    else
        log_success "Wszystkie procesy Kafka zatrzymane"
    fi
    
    if pgrep -f "order_simulator.py\|data_analyzer.py" > /dev/null; then
        log_warning "Niektóre procesy aplikacji nadal działają:"
        pgrep -f "order_simulator.py\|data_analyzer.py" | while read pid; do
            echo "  PID: $pid - $(ps -p $pid -o command --no-headers)"
        done
    else
        log_success "Wszystkie procesy aplikacji zatrzymane"
    fi
}

main "$@"
