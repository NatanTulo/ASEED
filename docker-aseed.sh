#!/bin/bash
# ASEED - Docker Management Script
# Skrypt do zarządzania systemem ASEED w kontenerach Docker

set -e

echo "🐳 ASEED - System analizy zamówień w kontenerach Docker"
echo "======================================================="

# Kolory dla lepszej czytelności
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funkcja sprawdzania Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker nie jest zainstalowany${NC}"
        echo "Zainstaluj Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}Docker Compose nie jest zainstalowany${NC}"
        echo "Zainstaluj Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi

    echo -e "${GREEN}Docker: $(docker --version)${NC}"
    
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}Docker Compose: $(docker compose version --short)${NC}"
        DOCKER_COMPOSE_CMD="docker compose"
    else
        echo -e "${GREEN}Docker Compose: $(docker-compose --version | cut -d' ' -f3 | tr -d ',')${NC}"
        DOCKER_COMPOSE_CMD="docker-compose"
    fi
}

# Funkcja uruchamiania systemu
start_system() {
    echo -e "${BLUE}Uruchamianie systemu ASEED...${NC}"
    
    # Sprawdź czy kontenery już działają
    if $DOCKER_COMPOSE_CMD ps | grep -q "Up"; then
        echo -e "${YELLOW}Niektóre kontenery już działają. Zatrzymuję...${NC}"
        stop_system
        sleep 2
    fi
    
    # Uruchom wszystkie serwisy (Docker Compose zbuduje obrazy automatycznie jeśli nie istnieją)
    echo -e "${BLUE}Uruchamianie kontenerów...${NC}"
    $DOCKER_COMPOSE_CMD up -d
    
    # Sprawdź status
    echo -e "${BLUE}Sprawdzanie statusu kontenerów...${NC}"
    sleep 5
    show_status
    
    # Sprawdź czy Kafka topic został utworzony
    echo -e "${BLUE}📡 Sprawdzanie Kafka topic...${NC}"
    sleep 10
    create_kafka_topic
    
    echo ""
    echo -e "${GREEN}System ASEED uruchomiony pomyślnie!${NC}"
    echo ""
    echo -e "${BLUE}Dashboard: http://localhost:5005${NC}"
    echo -e "${BLUE}Spark UI: http://localhost:8080${NC}"
    echo -e "${BLUE}Logi: docker-compose logs -f [service]${NC}"
    echo -e "${BLUE}🛑 Zatrzymanie: ./docker-aseed.sh stop${NC}"
    echo -e "${BLUE}Jeśli niektóre kontenery się nie uruchamiają, upewnij się, że folder logs/ ma wymagane uprawnienia:${NC}"
    echo -e "${BLUE}sudo chmod 777 logs/${NC}"
    echo -e "${BLUE}Lub uruchom skrypt przy pomocy sudo:${NC}"
    echo -e "${BLUE}sudo ./docker-aseed.sh install ${NC}"
}

# Funkcja zatrzymywania systemu
stop_system() {
    echo -e "${YELLOW}🛑 Zatrzymywanie systemu ASEED...${NC}"
    
    $DOCKER_COMPOSE_CMD down --remove-orphans
    
    echo -e "${GREEN}System zatrzymany${NC}"
}

# Funkcja pokazywania statusu
show_status() {
    echo -e "${BLUE}Status kontenerów ASEED${NC}"
    echo "=========================="
    
    $DOCKER_COMPOSE_CMD ps
    
    echo ""
    echo -e "${BLUE}Woluminy:${NC}"
    docker volume ls | grep aseed || echo "Brak wolumenów ASEED"
    
    echo ""
    echo -e "${BLUE}Sieci:${NC}"
    docker network ls | grep aseed || echo "Brak sieci ASEED"
}

# Funkcja pokazywania logów
show_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        echo -e "${BLUE}Logi wszystkich serwisów:${NC}"
        $DOCKER_COMPOSE_CMD logs -f
    else
        echo -e "${BLUE}Logi serwisu $service:${NC}"
        $DOCKER_COMPOSE_CMD logs -f $service
    fi
}

# Funkcja restartu pojedynczego serwisu
restart_service() {
    local service=$1
    
    if [ -z "$service" ]; then
        echo -e "${RED}Podaj nazwę serwisu do restartu${NC}"
        echo "Dostępne serwisy: zookeeper, kafka, spark-master, order-simulator, data-analyzer, web-dashboard"
        return 1
    fi
    
    echo -e "${YELLOW}Restartowanie serwisu $service...${NC}"
    $DOCKER_COMPOSE_CMD restart $service
    
    echo -e "${GREEN}Serwis $service zrestartowany${NC}"
}

# Funkcja czyszczenia
cleanup() {
    echo -e "${YELLOW}🧹 Czyszczenie systemu ASEED...${NC}"
    
    # Zatrzymaj i usuń kontenery
    $DOCKER_COMPOSE_CMD down --remove-orphans --volumes
    
    # Usuń obrazy ASEED
    echo -e "${BLUE}Usuwanie obrazów ASEED...${NC}"
    docker images | grep aseed | awk '{print $3}' | xargs -r docker rmi -f
    
    # Usuń nieużywane woluminy i sieci
    docker system prune -f --volumes
    
    echo -e "${GREEN}System wyczyszczony${NC}"
}

# Funkcja tworzenia Kafka topic
create_kafka_topic() {
    echo -e "${BLUE}📡 Tworzenie Kafka topic 'orders'...${NC}"
    
    # Poczekaj na Kafka
    for i in {1..30}; do
        if docker exec aseed-kafka kafka-topics --list --bootstrap-server localhost:9092 >/dev/null 2>&1; then
            break
        fi
        echo "Czekam na Kafka... ($i/30)"
        sleep 2
    done
    
    # Utwórz topic
    docker exec aseed-kafka kafka-topics \
        --create \
        --topic orders \
        --bootstrap-server localhost:9092 \
        --partitions 3 \
        --replication-factor 1 \
        --if-not-exists
    
    echo -e "${GREEN}Topic 'orders' utworzony${NC}"
}

# Funkcja testowania
test_system() {
    local minutes=${1:-2}
    local rate=${2:-10}
    
    echo -e "${BLUE}Test systemu przez $minutes minut z $rate zamówień/min${NC}"
    
    # Uruchom dodatkowy kontener do testów
    docker run --rm --network aseed_aseed-network \
        -e KAFKA_BOOTSTRAP_SERVERS=kafka:29092 \
        -e TEST_MINUTES=$minutes \
        -e TEST_RATE=$rate \
        aseed_order-simulator:latest python src/test_data_generator.py --minutes $minutes --rate $rate
}

# Funkcja budowania obrazów
build_images() {
    echo -e "${BLUE}🔨 Budowanie obrazów Docker...${NC}"
    $DOCKER_COMPOSE_CMD build --no-cache --parallel
    echo -e "${GREEN}Obrazy zbudowane${NC}"
}

# Funkcja instalacji (nowa)
install_system() {
    echo -e "${BLUE}ASEED - Instalacja systemu Docker${NC}"
    echo "===================================="
    
    # Sprawdź Docker (z auto-instalacją wskazówek)
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker nie jest zainstalowany${NC}"
        echo ""
        echo "Instrukcje instalacji Docker:"
        echo "   Ubuntu/Debian: curl -fsSL https://get.docker.com | sh"
        echo "   Arch Linux: sudo pacman -S docker docker-compose"
        echo "   Fedora: sudo dnf install docker docker-compose"
        echo "   macOS/Windows: Pobierz Docker Desktop z https://docs.docker.com/get-docker/"
        echo ""
        echo "Po instalacji uruchom ponownie: ./docker-aseed.sh install"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}Docker Compose nie jest zainstalowany${NC}"
        echo "Zainstaluj Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi

    echo -e "${GREEN}Docker: $(docker --version)${NC}"
    
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}Docker Compose: $(docker compose version --short)${NC}"
        DOCKER_COMPOSE_CMD="docker compose"
    else
        echo -e "${GREEN}Docker Compose: $(docker-compose --version | cut -d' ' -f3 | tr -d ',')${NC}"
        DOCKER_COMPOSE_CMD="docker-compose"
    fi
    
    # Sprawdź czy Docker daemon działa
    if ! docker ps &> /dev/null; then
        echo -e "${YELLOW}Docker daemon nie działa. Uruchamianie...${NC}"
        
        # Próba automatycznego uruchomienia
        if command -v systemctl &> /dev/null; then
            sudo systemctl start docker || {
                echo -e "${RED}Nie można uruchomić Docker daemon${NC}"
                echo "Spróbuj ręcznie: sudo systemctl start docker"
                exit 1
            }
        else
            echo -e "${RED}Docker daemon nie działa${NC}"
            echo "Uruchom Docker Desktop lub użyj: sudo systemctl start docker"
            exit 1
        fi
    fi
    
    # Sprawdź wymagania systemowe
    echo -e "${BLUE}Sprawdzanie wymagań systemowych...${NC}"
    
    # Sprawdź dostępną pamięć (minimum 4GB)
    if command -v free &> /dev/null; then
        total_mem=$(free -g | awk 'NR==2{print $2}')
        if [ "$total_mem" -lt 4 ]; then
            echo -e "${YELLOW}Mało pamięci RAM: ${total_mem}GB (zalecane: 4GB+)${NC}"
        else
            echo -e "${GREEN}Pamięć RAM: ${total_mem}GB${NC}"
        fi
    fi
    
    # Sprawdź dostępne porty
    echo -e "${BLUE}Sprawdzanie portów...${NC}"
    ports_to_check=(5005 8080 9092 2181)
    for port in "${ports_to_check[@]}"; do
        if command -v lsof &> /dev/null && lsof -i :$port &> /dev/null; then
            echo -e "${YELLOW}Port $port jest zajęty${NC}"
        else
            echo -e "${GREEN}Port $port dostępny${NC}"
        fi
    done
    
    # Dodaj użytkownika do grupy docker (jeśli potrzeba)
    if ! groups | grep -q docker && [ -S /var/run/docker.sock ]; then
        echo -e "${YELLOW}Dodanie użytkownika do grupy docker...${NC}"
        sudo usermod -aG docker $USER
        echo -e "${BLUE}Wyloguj się i zaloguj ponownie, aby zmiany zostały zastosowane${NC}"
        echo "   Lub użyj: newgrp docker"
    fi
    
    # Utwórz katalogi robocze
    echo -e "${BLUE}Tworzenie katalogów...${NC}"
    mkdir -p logs
    sudo chmod 777 logs/

    # Test Docker Compose
    echo -e "${BLUE}Test konfiguracji Docker Compose...${NC}"
    if ! $DOCKER_COMPOSE_CMD config &> /dev/null; then
        echo -e "${RED}Błąd w pliku docker-compose.yml${NC}"
        $DOCKER_COMPOSE_CMD config
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}Instalacja zakończona pomyślnie!${NC}"
    echo ""
    echo -e "${BLUE}Następne kroki:${NC}"
    echo "   1. ./docker-aseed.sh start      # Uruchom system"
    echo "   2. http://localhost:5005        # Otwórz dashboard"
    echo "   3. ./docker-aseed.sh logs       # Monitoruj system"
    echo "   4. ./docker-aseed.sh stop       # Zatrzymaj gdy skończysz"
    echo ""
    echo -e "${BLUE}Pomoc:${NC} ./docker-aseed.sh help"
}

# Main logic
case "${1:-help}" in
    install)
        install_system
        ;;
    start)
        check_docker
        start_system
        ;;
    stop)
        check_docker
        stop_system
        ;;
    restart)
        check_docker
        stop_system
        sleep 2
        start_system
        ;;
    status)
        check_docker
        show_status
        ;;
    logs)
        check_docker
        show_logs $2
        ;;
    restart-service)
        check_docker
        restart_service $2
        ;;
    test)
        check_docker
        test_system $2 $3
        ;;
    build)
        check_docker
        build_images
        ;;
    cleanup)
        check_docker
        cleanup
        ;;
    help|*)
        echo "🐳 ASEED Docker Management Script"
        echo ""
        echo "Użycie: $0 [komenda] [opcje]"
        echo ""
        echo "Komendy:"
        echo "  install            Zainstaluj i skonfiguruj system (uruchom najpierw!)"
        echo "  start              Uruchom cały system"
        echo "  stop               Zatrzymaj system"
        echo "  restart            Zrestartuj system"
        echo "  status             Pokaż status kontenerów"
        echo "  logs [service]     Pokaż logi (wszystkie lub konkretnego serwisu)"
        echo "  restart-service <service>  Zrestartuj konkretny serwis"
        echo "  test [min] [rate]  Uruchom test (domyślnie: 2 min, 10 zamówień/min)"
        echo "  build              Zbuduj obrazy Docker"
        echo "  cleanup            Wyczyść system (usuń kontenery, obrazy, woluminy)"
        echo "  help               Pokaż pomoc"
        echo ""
        echo "Quick Start:"
        echo "  $0 install                  # Jednorazowa instalacja"
        echo "  $0 start                    # Uruchom system"
        echo "  $0 logs web-dashboard       # Logi dashboardu"
        echo "  $0 test 5 20                # Test: 5 min, 20 zamówień/min"
        echo ""
        echo "Po uruchomieniu:"
        echo "  Dashboard: http://localhost:5005"
        echo "  Spark UI: http://localhost:8080"
        ;;
esac
