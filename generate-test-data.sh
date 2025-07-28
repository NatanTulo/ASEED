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

echo "🧪 Generator danych testowych dla Web Dashboard"
echo "=============================================="
echo ""

# Sprawdź czy wirtualne środowisko istnieje
if [ ! -d "venv" ]; then
    log_error "Wirtualne środowisko Python nie istnieje. Uruchom najpierw ./install.sh"
    exit 1
fi

# Aktywuj wirtualne środowisko
source venv/bin/activate

# Utwórz katalog logs jeśli nie istnieje
mkdir -p logs

log_info "Generowanie przykładowych danych zamówień..."
log_info "To pomoże przetestować wizualizacje w Web Dashboard"
echo ""

# Domyślne parametry
MINUTES=${1:-2}
RATE=${2:-6}

echo "Parametry:"
echo "- Czas: $MINUTES minut"
echo "- Częstotliwość: $RATE zamówień/minutę"
echo "- Łączne zamówienia: $((MINUTES * RATE))"
echo ""

log_warning "Uwaga: To nadpisze istniejące logi order_simulator.log"
read -p "Czy kontynuować? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Anulowano"
    exit 0
fi

echo ""
log_info "Uruchamianie generatora..."

cd src
python test_data_generator.py --minutes $MINUTES --rate $RATE

echo ""
log_success "🎉 Dane testowe wygenerowane!"
echo ""
log_info "Aby zobaczyć efekty:"
log_info "1. Uruchom Web Dashboard: ./start-dashboard.sh"
log_info "2. Otwórz: http://localhost:5000"
log_info "3. Obejrzyj wykresy i statystyki w sekcji 'Analiza Zamówień'"
echo ""
log_info "Lub sprawdź logi:"
log_info "tail -f logs/order_simulator.log"
