#!/bin/bash

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funkcje pomocnicze
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_header() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 Online Store Order Analysis                  ║"
    echo "║                        DEMO GUIDE                           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

wait_for_key() {
    echo ""
    echo -e "${YELLOW}Naciśnij Enter aby kontynuować...${NC}"
    read
}

demo_step_1() {
    show_header
    echo -e "${BLUE}📋 KROK 1: Sprawdzenie wymagań systemu${NC}"
    echo "=========================================="
    echo ""
    echo "Najpierw sprawdzimy czy Twój system ma wszystkie wymagane komponenty:"
    echo "• Java 11+"
    echo "• Python 3 z pip" 
    echo "• 4GB RAM"
    echo "• 2GB wolnego miejsca na dysku"
    echo "• Połączenie internetowe"
    echo ""
    
    wait_for_key
    
    echo "Uruchamiam sprawdzenie wymagań..."
    echo ""
    ./check-requirements.sh
    
    wait_for_key
}

demo_step_2() {
    show_header
    echo -e "${BLUE}📦 KROK 2: Instalacja wszystkich zależności${NC}"
    echo "============================================="
    echo ""
    echo "Teraz zainstalujemy wszystkie potrzebne komponenty:"
    echo "• Apache Kafka 3.6.0 (system kolejek wiadomości)"
    echo "• Apache Spark 3.5.0 (silnik analizy strumieniowej)"
    echo "• Wirtualne środowisko Python z bibliotekami"
    echo ""
    echo "Ta operacja może potrwać 5-10 minut w zależności od prędkości internetu."
    echo ""
    
    wait_for_key
    
    echo "Uruchamiam instalację..."
    echo ""
    ./install.sh
    
    if [ $? -eq 0 ]; then
        log_success "Instalacja zakończona pomyślnie!"
    else
        log_warning "Wystąpił problem z instalacją. Sprawdź komunikaty powyżej."
        exit 1
    fi
    
    wait_for_key
}

demo_step_3() {
    show_header
    echo -e "${BLUE}🚀 KROK 3: Uruchomienie systemu${NC}"
    echo "================================="
    echo ""
    echo "Uruchomimy teraz cały system składający się z:"
    echo "• Zookeeper (koordynacja Kafka)"
    echo "• Kafka (broker wiadomości)"
    echo "• Order Simulator (generator zamówień)"
    echo "• Data Analyzer (analizator Spark)"
    echo ""
    echo "System potrzebuje 2-3 minut na pełne uruchomienie."
    echo ""
    
    wait_for_key
    
    echo "Uruchamiam system..."
    echo ""
    ./start.sh
    
    if [ $? -eq 0 ]; then
        log_success "System uruchomiony pomyślnie!"
    else
        log_warning "Wystąpił problem z uruchomieniem. Sprawdź komunikaty powyżej."
        exit 1
    fi
    
    wait_for_key
}

demo_step_4() {
    show_header
    echo -e "${BLUE}📊 KROK 4: Monitorowanie systemu${NC}"
    echo "================================="
    echo ""
    echo "System jest teraz uruchomiony! Oto co możesz zrobić:"
    echo ""
    echo -e "${GREEN}🌐 NOWOŚĆ - Web Dashboard (ZALECANE):${NC}"
    echo "   ./start-dashboard.sh"
    echo "   Następnie otwórz: http://localhost:5000"
    echo "   • Monitorowanie w czasie rzeczywistym"
    echo "   • Zarządzanie serwisami przez GUI"
    echo "   • Podgląd logów i konfiguracji"
    echo ""
    echo -e "${BLUE}Tradycyjne monitorowanie:${NC}"
    echo "1. Obejrzeć analizy w czasie rzeczywistym:"
    echo "   tail -f logs/data_analyzer.log"
    echo ""
    echo "2. Monitorować generowane zamówienia:"
    echo "   tail -f logs/order_simulator.log"
    echo ""
    echo "3. Użyć interaktywnego monitora:"
    echo "   ./monitor.sh"
    echo ""
    echo "4. Sprawdzić status wszystkich procesów:"
    echo "   make status"
    echo ""
    
    wait_for_key
    
    # Oferuj użytkownikowi wybór
    echo -e "${YELLOW}Czy chcesz uruchomić Web Dashboard teraz? (y/n)${NC}"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Uruchamianie Web Dashboard..."
        echo "Otwórz http://localhost:5000 w przeglądarce"
        echo "Naciśnij Ctrl+C w tym terminalu aby zatrzymać dashboard"
        ./start-dashboard.sh
        return
    fi
    
    echo "Sprawdzamy status systemu..."
    echo ""
    make status
    
    wait_for_key
}

demo_step_5() {
    show_header
    echo -e "${BLUE}🔍 KROK 5: Podgląd wyników analizy${NC}"
    echo "=================================="
    echo ""
    echo "Pokażemy teraz ostatnie wyniki analizy danych."
    echo "System analizuje zamówienia w oknach czasowych i pokazuje:"
    echo "• Top produkty według liczby zamówień"
    echo "• Przychody z sprzedaży"
    echo "• Analizę kategorii produktów"
    echo ""
    
    wait_for_key
    
    if [ -f "logs/data_analyzer.log" ]; then
        echo "Ostatnie wyniki analizy:"
        echo "========================"
        tail -n 50 logs/data_analyzer.log | grep -E "(TOP PRODUKTY|Kategoria|Zamówienia:|Przychód:|===)"
    else
        log_warning "Logi analizy jeszcze nie istnieją. System potrzebuje więcej czasu na uruchomienie."
        echo ""
        echo "Spróbuj ponownie za 2-3 minuty:"
        echo "tail -f logs/data_analyzer.log"
    fi
    
    wait_for_key
}

demo_step_6() {
    show_header
    echo -e "${BLUE}⚙️  KROK 6: Konfiguracja systemu${NC}"
    echo "================================"
    echo ""
    echo "Możesz dostosować działanie systemu edytując plik .env:"
    echo ""
    cat .env
    echo ""
    echo "Dostępne opcje:"
    echo "• ORDERS_PER_SECOND - ile zamówień na sekundę generować"
    echo "• PRODUCT_COUNT - ile różnych produktów w katalogu"
    echo "• SPARK_MASTER_URL - tryb działania Spark"
    echo ""
    echo "Po zmianie konfiguracji zrestartuj system:"
    echo "  ./stop.sh && ./start.sh"
    echo ""
    
    wait_for_key
}

demo_step_7() {
    show_header
    echo -e "${BLUE}🛠️  KROK 7: Przydatne komendy${NC}"
    echo "==============================="
    echo ""
    echo "Oto najważniejsze komendy do zarządzania systemem:"
    echo ""
    echo -e "${GREEN}Zarządzanie systemem:${NC}"
    echo "  ./start.sh           - uruchom system"
    echo "  ./stop.sh            - zatrzymaj system"  
    echo "  ./monitor.sh         - interaktywny monitor"
    echo "  make status          - sprawdź status procesów"
    echo "  make restart         - zrestartuj system"
    echo ""
    echo -e "${GREEN}Monitorowanie:${NC}"
    echo "  tail -f logs/data_analyzer.log    - wyniki analiz"
    echo "  tail -f logs/order_simulator.log  - generowane zamówienia"
    echo "  tail -f logs/kafka.log            - logi Kafka"
    echo ""
    echo -e "${GREEN}Utrzymanie:${NC}"
    echo "  make clean           - wyczyść logi"
    echo "  ./check-requirements.sh - sprawdź wymagania"
    echo ""
    
    wait_for_key
}

demo_finish() {
    show_header
    echo -e "${GREEN}🎉 DEMO ZAKOŃCZONE POMYŚLNIE!${NC}"
    echo "=============================="
    echo ""
    echo "System Online Store Order Analysis jest teraz gotowy do użycia!"
    echo ""
    echo -e "${BLUE}Co dalej?${NC}"
    echo "• System będzie działał w tle i generował analizy"
    echo "• Sprawdzaj wyniki: tail -f logs/data_analyzer.log"
    echo "• Eksperymentuj z konfiguracją w pliku .env"
    echo "• Przeczytaj dokumentację w README.md"
    echo "• W razie problemów zobacz TROUBLESHOOTING.md"
    echo ""
    echo -e "${YELLOW}Aby zatrzymać system:${NC}"
    echo "  ./stop.sh"
    echo ""
    echo -e "${YELLOW}Aby uruchomić ponownie:${NC}"
    echo "  ./start.sh"
    echo ""
    echo "Dziękujemy za skorzystanie z naszego systemu! 🚀"
    echo ""
}

main() {
    echo -e "${CYAN}Witaj w demo systemu Online Store Order Analysis!${NC}"
    echo ""
    echo "Ten przewodnik przeprowadzi Cię przez:"
    echo "1. Sprawdzenie wymagań systemu"
    echo "2. Instalację wszystkich komponentów"  
    echo "3. Uruchomienie systemu"
    echo "4. Monitorowanie działania"
    echo "5. Podgląd wyników"
    echo "6. Konfigurację"
    echo "7. Przydatne komendy"
    echo ""
    echo "Całość zajmie około 15-20 minut."
    echo ""
    
    wait_for_key
    
    demo_step_1
    demo_step_2  
    demo_step_3
    demo_step_4
    demo_step_5
    demo_step_6
    demo_step_7
    demo_finish
}

# Sprawdź czy skrypt jest uruchamiany z właściwego katalogu
if [ ! -f "install.sh" ] || [ ! -f "start.sh" ]; then
    echo -e "${RED}❌ Błąd: Uruchom ten skrypt z głównego katalogu projektu ASEED${NC}"
    exit 1
fi

main "$@"
