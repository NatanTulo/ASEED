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

# Sprawdź czy wirtualne środowisko istnieje
if [ ! -d "venv" ]; then
    log_error "Wirtualne środowisko Python nie istnieje. Uruchom najpierw ./install.sh"
    exit 1
fi

# Aktywuj wirtualne środowisko
source venv/bin/activate

# Sprawdź czy wymagane pakiety są zainstalowane
log_info "Sprawdzanie wymaganych pakietów dla Web Dashboard..."

REQUIRED_PACKAGES=("flask" "flask-socketio" "psutil")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! pip show "$package" >/dev/null 2>&1; then
        MISSING_PACKAGES+=("$package")
    fi
done

# Zainstaluj brakujące pakiety
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    log_info "Instalowanie brakujących pakietów: ${MISSING_PACKAGES[*]}"
    pip install flask flask-socketio psutil
    log_success "Pakiety zainstalowane"
fi

# Utwórz katalogi jeśli nie istnieją
mkdir -p logs pids

# Uruchom Web Dashboard
log_info "Uruchamianie Web Dashboard..."
log_success "Dashboard dostępny na: http://localhost:5000"
log_info "Naciśnij Ctrl+C aby zatrzymać"

cd src
python web_dashboard.py
