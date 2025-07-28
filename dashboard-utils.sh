#!/bin/bash

# Skrypt pomocniczy do zarządzania PID files dla Web Dashboard

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

# Funkcje pomocnicze dla Web Dashboard
create_pid_file() {
    local service_name=$1
    local pid=$2
    local pids_dir="pids"
    
    mkdir -p "$pids_dir"
    echo "$pid" > "$pids_dir/$service_name.pid"
    log_info "Utworzono PID file dla $service_name: $pid"
}

remove_pid_file() {
    local service_name=$1
    local pids_dir="pids"
    
    if [ -f "$pids_dir/$service_name.pid" ]; then
        rm "$pids_dir/$service_name.pid"
        log_info "Usunięto PID file dla $service_name"
    fi
}

check_pid_file() {
    local service_name=$1
    local pids_dir="pids"
    
    if [ -f "$pids_dir/$service_name.pid" ]; then
        local pid=$(cat "$pids_dir/$service_name.pid")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "running:$pid"
        else
            rm "$pids_dir/$service_name.pid"
            echo "stopped:0"
        fi
    else
        echo "stopped:0"
    fi
}

# Export funkcji dla innych skryptów
export -f create_pid_file
export -f remove_pid_file  
export -f check_pid_file
