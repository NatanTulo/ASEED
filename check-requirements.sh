#!/bin/bash

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 Sprawdzanie wymagań systemu Online Store Order Analysis"
echo "========================================================="
echo ""

# Funkcje pomocnicze
check_passed=0
check_failed=0

log_check() {
    echo -n "🔍 Sprawdzanie $1... "
}

log_pass() {
    echo -e "${GREEN}✅ PASS${NC}"
    ((check_passed++))
}

log_fail() {
    echo -e "${RED}❌ FAIL${NC} - $1"
    ((check_failed++))
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Sprawdź system operacyjny
check_os() {
    log_check "systemu operacyjnego"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_pass
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            log_info "System: $NAME $VERSION_ID"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_pass
        log_info "System: macOS $(sw_vers -productVersion)"
    else
        log_fail "Nieobsługiwany system operacyjny: $OSTYPE"
    fi
}

# Sprawdź dostępność pamięci RAM
check_memory() {
    log_check "dostępnej pamięci RAM"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        total_mem=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$total_mem" -ge 4 ]; then
            log_pass
            log_info "Dostępna pamięć: ${total_mem}GB (wymagane: 4GB)"
        else
            log_fail "Za mało pamięci RAM: ${total_mem}GB (wymagane: 4GB)"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        total_mem=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
        if [ "$total_mem" -ge 4 ]; then
            log_pass
            log_info "Dostępna pamięć: ${total_mem}GB (wymagane: 4GB)"
        else
            log_fail "Za mało pamięci RAM: ${total_mem}GB (wymagane: 4GB)"
        fi
    else
        log_fail "Nie można sprawdzić ilości pamięci"
    fi
}

# Sprawdź dostępność miejsca na dysku
check_disk_space() {
    log_check "miejsca na dysku"
    
    available_space=$(df . | awk 'NR==2 {print int($4/1024/1024)}')
    if [ "$available_space" -ge 2 ]; then
        log_pass
        log_info "Dostępne miejsce: ${available_space}GB (wymagane: 2GB)"
    else
        log_fail "Za mało miejsca na dysku: ${available_space}GB (wymagane: 2GB)"
    fi
}

# Sprawdź Java
check_java() {
    log_check "instalacji Java"
    
    if command -v java &> /dev/null; then
        java_version=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
        java_major=$(echo $java_version | cut -d'.' -f1)
        
        if [ "$java_major" -ge 11 ]; then
            log_pass
            log_info "Wersja Java: $java_version"
        else
            log_fail "Java w wersji 11+ jest wymagana (znaleziono: $java_version)"
        fi
    else
        log_fail "Java nie jest zainstalowana"
    fi
}

# Sprawdź Python
check_python() {
    log_check "instalacji Python"
    
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        log_pass
        log_info "Wersja Python: $python_version"
    else
        log_fail "Python 3 nie jest zainstalowany"
    fi
}

# Sprawdź pip
check_pip() {
    log_check "instalacji pip"
    
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        log_pass
    else
        log_fail "pip nie jest zainstalowany"
    fi
}

# Sprawdź narzędzia systemowe
check_system_tools() {
    local tools=("wget" "curl" "tar")
    
    for tool in "${tools[@]}"; do
        log_check "narzędzia $tool"
        if command -v "$tool" &> /dev/null; then
            log_pass
        else
            log_fail "$tool nie jest zainstalowany"
        fi
    done
}

# Sprawdź porty
check_ports() {
    local ports=(2181 9092)
    
    for port in "${ports[@]}"; do
        log_check "dostępności portu $port"
        
        if command -v netstat &> /dev/null; then
            if netstat -ln | grep -q ":$port "; then
                log_fail "Port $port jest już używany"
            else
                log_pass
            fi
        elif command -v ss &> /dev/null; then
            if ss -ln | grep -q ":$port "; then
                log_fail "Port $port jest już używany"
            else
                log_pass
            fi
        else
            log_fail "Nie można sprawdzić portu (brak netstat/ss)"
        fi
    done
}

# Sprawdź połączenie internetowe
check_internet() {
    log_check "połączenia internetowego"
    
    if curl -s --head --request GET https://www.google.com | grep "200 OK" > /dev/null; then
        log_pass
    else
        log_fail "Brak połączenia internetowego (wymagane do pobrania Kafka/Spark)"
    fi
}

# Podsumowanie
show_summary() {
    echo ""
    echo "=============================="
    echo "PODSUMOWANIE SPRAWDZENIA"
    echo "=============================="
    echo ""
    
    if [ $check_failed -eq 0 ]; then
        echo -e "${GREEN}✅ Wszystkie sprawdzenia przeszły pomyślnie!${NC}"
        echo ""
        echo -e "${BLUE}💡 System jest gotowy do instalacji${NC}"
        echo "   Uruchom: ./install.sh"
    else
        echo -e "${RED}❌ Niektóre sprawdzenia nie powiodły się${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Sprawdzenia zakończone:${NC}"
        echo "   ✅ Pomyślne: $check_passed"
        echo "   ❌ Niepomyślne: $check_failed"
        echo ""
        echo -e "${BLUE}💡 Rekomendacje:${NC}"
        
        if ! command -v java &> /dev/null; then
            echo "   - Zainstaluj Java 11+: sudo apt install openjdk-11-jdk (Ubuntu/Debian)"
        fi
        
        if ! command -v python3 &> /dev/null; then
            echo "   - Zainstaluj Python 3: sudo apt install python3 python3-pip (Ubuntu/Debian)"
        fi
        
        if ! command -v wget &> /dev/null; then
            echo "   - Zainstaluj wget: sudo apt install wget (Ubuntu/Debian)"
        fi
        
        if ! command -v curl &> /dev/null; then
            echo "   - Zainstaluj curl: sudo apt install curl (Ubuntu/Debian)"
        fi
        
        echo ""
        echo -e "${YELLOW}   Po naprawieniu problemów uruchom ponownie: ./check-requirements.sh${NC}"
    fi
}

# Główna funkcja
main() {
    check_os
    check_memory
    check_disk_space
    check_java
    check_python
    check_pip
    check_system_tools
    check_ports
    check_internet
    
    show_summary
}

main "$@"
