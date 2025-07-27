#!/bin/bash

set -e  # Zatrzymaj skrypt przy błędzie

echo "🚀 Instalacja Online Store Order Analysis (bez Docker)"
echo "===================================================="
echo ""

# Kolory dla lepszej czytelności
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Sprawdź system operacyjny
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$NAME
            DISTRO=$ID
        else
            log_error "Nie można określić dystrybucji Linux"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        DISTRO="macos"
    else
        log_error "Nieobsługiwany system operacyjny: $OSTYPE"
        exit 1
    fi
    
    log_info "System: $OS"
}

# Sprawdź czy skrypt jest uruchamiany jako root (jeśli potrzebne)
check_sudo() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Skrypt jest uruchamiany jako root. To może być niebezpieczne."
        read -p "Czy chcesz kontynuować? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Instalacja Java (wymagana dla Kafka i Spark)
install_java() {
    log_info "Sprawdzanie instalacji Java..."
    
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
        log_success "Java już zainstalowana: $JAVA_VERSION"
        return
    fi
    
    log_info "Instalowanie Java 11..."
    
    if [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "debian" ]]; then
        sudo apt update
        sudo apt install -y openjdk-11-jdk
    elif [[ "$DISTRO" == "fedora" ]] || [[ "$DISTRO" == "centos" ]] || [[ "$DISTRO" == "rhel" ]]; then
        sudo dnf install -y java-11-openjdk-devel || sudo yum install -y java-11-openjdk-devel
    elif [[ "$DISTRO" == "arch" ]]; then
        sudo pacman -S --noconfirm jdk11-openjdk
    elif [[ "$DISTRO" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install openjdk@11
        else
            log_error "Homebrew nie jest zainstalowany. Zainstaluj Java 11 ręcznie."
            exit 1
        fi
    else
        log_error "Nieobsługiwana dystrybucja dla automatycznej instalacji Java"
        exit 1
    fi
    
    log_success "Java zainstalowana"
}

# Instalacja Python i pip
install_python() {
    log_info "Sprawdzanie instalacji Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        log_success "Python już zainstalowany: $PYTHON_VERSION"
    else
        log_info "Instalowanie Python 3..."
        
        if [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "debian" ]]; then
            sudo apt install -y python3 python3-pip python3-venv
        elif [[ "$DISTRO" == "fedora" ]] || [[ "$DISTRO" == "centos" ]] || [[ "$DISTRO" == "rhel" ]]; then
            sudo dnf install -y python3 python3-pip || sudo yum install -y python3 python3-pip
        elif [[ "$DISTRO" == "arch" ]]; then
            sudo pacman -S --noconfirm python python-pip
        elif [[ "$DISTRO" == "macos" ]]; then
            if command -v brew &> /dev/null; then
                brew install python
            else
                log_error "Homebrew nie jest zainstalowany. Zainstaluj Python 3 ręcznie."
                exit 1
            fi
        fi
        
        log_success "Python zainstalowany"
    fi
}

# Tworzenie wirtualnego środowiska Python
create_venv() {
    log_info "Tworzenie wirtualnego środowiska Python..."
    
    if [ -d "venv" ]; then
        log_info "Wirtualne środowisko już istnieje"
    else
        python3 -m venv venv
        log_success "Wirtualne środowisko utworzone"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
}

# Instalacja pakietów Python
install_python_packages() {
    log_info "Instalowanie pakietów Python..."
    
    source venv/bin/activate
    
    # Instaluj pyspark z odpowiednimi bibliotekami
    pip install pyspark[sql]==3.5.0
    pip install kafka-python==2.0.2
    pip install faker==19.6.2
    
    log_success "Pakiety Python zainstalowane"
}

# Pobieranie i instalacja Kafka
install_kafka() {
    log_info "Instalowanie Apache Kafka..."
    
    KAFKA_VERSION="2.13-3.9.0"
    KAFKA_DIR="kafka_$KAFKA_VERSION"
    
    if [ -d "$KAFKA_DIR" ]; then
        log_info "Kafka już zainstalowana"
        return
    fi
    
    log_info "Pobieranie Kafka $KAFKA_VERSION..."
    
    # Lista dostępnych mirror-ów
    MIRRORS=(
        "https://downloads.apache.org/kafka/3.9.0/kafka_$KAFKA_VERSION.tgz"
        "https://archive.apache.org/dist/kafka/3.9.0/kafka_$KAFKA_VERSION.tgz"
        "https://dlcdn.apache.org/kafka/3.9.0/kafka_$KAFKA_VERSION.tgz"
    )
    
    # Próbuj każdy mirror
    for mirror in "${MIRRORS[@]}"; do
        log_info "Próbuję pobrać z: $mirror"
        if wget -q --timeout=30 --tries=3 "$mirror"; then
            log_success "Pomyślnie pobrano Kafka"
            break
        else
            log_warning "Nie udało się pobrać z tego mirror-a, próbuję następny..."
        fi
    done
    
    # Sprawdź czy plik został pobrany
    if [ ! -f "kafka_$KAFKA_VERSION.tgz" ]; then
        log_error "Nie udało się pobrać Kafka z żadnego mirror-a"
        exit 1
    fi
    
    tar -xzf "kafka_$KAFKA_VERSION.tgz"
    rm "kafka_$KAFKA_VERSION.tgz"
    
    log_success "Kafka zainstalowana w $KAFKA_DIR"
}

# Pobieranie i instalacja Spark
install_spark() {
    log_info "Instalowanie Apache Spark..."
    
    SPARK_VERSION="3.5.0"
    HADOOP_VERSION="3"
    SPARK_DIR="spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION"
    
    if [ -d "$SPARK_DIR" ]; then
        log_info "Spark już zainstalowana"
        return
    fi
    
    log_info "Pobieranie Spark $SPARK_VERSION..."
    
    # Spróbuj różne źródła dla Spark
    SPARK_URLS=(
        "https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/$SPARK_DIR.tgz"
        "https://dlcdn.apache.org/spark/spark-$SPARK_VERSION/$SPARK_DIR.tgz"
    )
    
    SPARK_DOWNLOADED=false
    for url in "${SPARK_URLS[@]}"; do
        log_info "Próba pobrania z: $url"
        if wget -q "$url"; then
            SPARK_DOWNLOADED=true
            break
        else
            log_warning "Nie udało się pobrać z: $url"
        fi
    done
    
    if [ "$SPARK_DOWNLOADED" = false ]; then
        log_error "Nie udało się pobrać Spark z żadnego źródła"
        log_info "Spróbuj pobrać ręcznie i wypakować: $SPARK_DIR.tgz"
        exit 1
    fi
    
    tar -xzf "$SPARK_DIR.tgz"
    rm "$SPARK_DIR.tgz"
    
    log_success "Spark zainstalowana w $SPARK_DIR"
}

# Instalacja narzędzi systemowych
install_system_tools() {
    log_info "Instalowanie narzędzi systemowych..."
    
    if [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "debian" ]]; then
        sudo apt update
        sudo apt install -y wget curl unzip
    elif [[ "$DISTRO" == "fedora" ]] || [[ "$DISTRO" == "centos" ]] || [[ "$DISTRO" == "rhel" ]]; then
        sudo dnf install -y wget curl unzip || sudo yum install -y wget curl unzip
    elif [[ "$DISTRO" == "arch" ]]; then
        sudo pacman -S --noconfirm wget curl unzip
    elif [[ "$DISTRO" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            log_info "Instalowanie Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install wget curl
    fi
    
    log_success "Narzędzia systemowe zainstalowane"
}

# Tworzenie plików konfiguracyjnych
create_config_files() {
    log_info "Tworzenie plików konfiguracyjnych..."
    
    # Plik .env z konfiguracją
    cat > .env << EOF
# Konfiguracja Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=orders

# Konfiguracja symulatora
ORDERS_PER_SECOND=2
PRODUCT_COUNT=50

# Konfiguracja Spark
SPARK_MASTER_URL=local[*]
EOF

    log_success "Pliki konfiguracyjne utworzone"
}

# Główna funkcja instalacji
main() {
    log_info "Rozpoczynanie instalacji..."
    
    detect_os
    check_sudo
    install_system_tools
    install_java
    install_python
    create_venv
    install_python_packages
    install_kafka
    install_spark
    create_config_files
    
    echo ""
    log_success "🎉 Instalacja zakończona pomyślnie!"
    echo ""
    log_info "Aby uruchomić projekt:"
    log_info "1. ./start.sh  - uruchom wszystkie serwisy"
    log_info "2. ./monitor.sh - monitoruj działanie"
    log_info "3. ./stop.sh - zatrzymaj serwisy"
    echo ""
    log_warning "Uwaga: Pierwsze uruchomienie może potrwać kilka minut"
}

# Uruchom instalację
main "$@"
