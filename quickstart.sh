#!/bin/bash

echo "🚀 Szybki start Online Store Order Analysis"
echo "==========================================="
echo ""

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

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Sprawdź czy skrypty istnieją
if [ ! -f "install.sh" ] || [ ! -f "start.sh" ]; then
    log_error "Nie można znaleźć wymaganych skryptów w bieżącym katalogu"
    exit 1
fi

log_info "Krok 1/3: Sprawdzanie wymagań systemu..."
if [ -f "check-requirements.sh" ]; then
    ./check-requirements.sh
    if [ $? -ne 0 ]; then
        log_error "Sprawdzenie wymagań nie powiodło się"
        echo ""
        echo "Przeczytaj komunikaty powyżej i napraw problemy przed kontynuacją."
        exit 1
    fi
else
    log_info "Pomijanie sprawdzenia wymagań (plik nie istnieje)"
fi

echo ""
log_info "Krok 2/3: Instalacja zależności..."
./install.sh
if [ $? -ne 0 ]; then
    log_error "Instalacja nie powiodła się"
    exit 1
fi

echo ""
log_info "Krok 3/3: Uruchomienie systemu..."
./start.sh
if [ $? -ne 0 ]; then
    log_error "Uruchomienie systemu nie powiodło się"
    exit 1
fi

echo ""
log_success "🎉 Szybki start zakończony pomyślnie!"
echo ""
echo "System jest teraz uruchomiony. Aby go monitorować:"
echo "  ./monitor.sh"
echo ""
echo "Aby zatrzymać system:"
echo "  ./stop.sh"
