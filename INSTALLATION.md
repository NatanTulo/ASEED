# Installation Guide

## 📋 Wymagania systemu

### Minimalne wymagania:
- **4GB RAM** (8GB zalecane)
- **2GB wolnego miejsca na dysku** 
- **Internet** (do pobierania komponentów)
- **Linux/macOS** (testowane na Ubuntu 20.04+, macOS 10.15+)

### Automatycznie instalowane komponenty:
- Java 11+ (OpenJDK)
- Python 3.8+ z pip
- Apache Kafka 3.9.0
- Apache Spark 3.5.0
- Biblioteki Python: pyspark, kafka-python, faker

## 🚀 Metody instalacji

### Metoda 1: Interaktywne demo (ZALECANE)

Najlepsza dla nowych użytkowników - przeprowadzi Cię przez każdy krok:

```bash
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED
./demo.sh
```

### Metoda 2: Automatyczna instalacja

Szybka instalacja wszystkiego jedną komendą:

```bash
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED
./quickstart.sh
```

### Metoda 3: Krok po kroku

Pełna kontrola nad procesem instalacji:

```bash
# 1. Pobierz projekt
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED

# 2. Sprawdź wymagania
./check-requirements.sh

# 3. Zainstaluj zależności
./install.sh

# 4. Uruchom system
./start.sh

# 5. Monitoruj
./monitor.sh
```

### Metoda 4: Używając Makefile

```bash
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED

make check      # sprawdź wymagania
make install    # zainstaluj
make start      # uruchom
make monitor    # monitoruj
```

## 🔧 Szczegóły instalacji

### Co się dzieje podczas instalacji:

1. **Sprawdzenie systemu operacyjnego**
   - Wykrycie dystrybucji Linux lub macOS
   - Sprawdzenie dostępnych zasobów

2. **Instalacja Java 11**
   - Ubuntu/Debian: `openjdk-11-jdk`
   - CentOS/RHEL/Fedora: `java-11-openjdk-devel`
   - macOS: `openjdk@11` przez Homebrew

3. **Instalacja Python i pip**
   - Ubuntu/Debian: `python3 python3-pip python3-venv`
   - CentOS/RHEL/Fedora: `python3 python3-pip`
   - macOS: `python` przez Homebrew

4. **Tworzenie środowiska Python**
   - Utworzenie `venv/` w katalogu projektu
   - Instalacja pakietów z `requirements.txt`

5. **Pobieranie Apache Kafka**
   - Download z oficjalnego mirror: `kafka_2.13-3.9.0.tgz`
   - Rozpakowanie do `kafka_2.13-3.9.0/`

6. **Pobieranie Apache Spark**
   - Download z oficjalnego mirror: `spark-3.5.0-bin-hadoop3.tgz`
   - Rozpakowanie do `spark-3.5.0-bin-hadoop3/`

7. **Konfiguracja środowiska**
   - Utworzenie pliku `.env` z domyślnymi ustawieniami

## 🎯 Sprawdzenie instalacji

Po instalacji sprawdź czy wszystko działa:

```bash
# Sprawdź status systemu
make status

# Lub ręcznie:
./monitor.sh  # wybierz opcję 5
```

Powinny być uruchomione procesy:
- ✅ Zookeeper (port 2181)
- ✅ Kafka (port 9092) 
- ✅ Order Simulator
- ✅ Data Analyzer

## 🐛 Rozwiązywanie problemów

### Najczęstsze błędy instalacji:

#### 1. Brak uprawnień sudo
```bash
# Błąd: "sudo: command not found" lub brak uprawnień
```
**Rozwiązanie:** Zainstaluj sudo lub użyj konta root:
```bash
# CentOS/RHEL jako root:
yum install sudo
usermod -aG wheel username

# Ubuntu/Debian jako root:
apt install sudo  
usermod -aG sudo username
```

#### 2. Brak połączenia internetowego
```bash
# Błąd: Nie można pobrać komponentów
```
**Rozwiązanie:** Sprawdź proxy i firewall:
```bash
# Test połączenia
curl -I https://www.google.com

# Konfiguracja proxy (jeśli potrzebna)
export http_proxy=http://proxy:port
export https_proxy=https://proxy:port
```

#### 3. Zajęte porty
```bash
# Błąd: "Address already in use"
```
**Rozwiązanie:** Sprawdź i zwolnij porty:
```bash
# Sprawdź co używa portów
netstat -tlnp | grep -E ':(2181|9092)'

# Zatrzymaj inne procesy Kafka/Zookeeper
pkill -f kafka
pkill -f zookeeper

# Lub zmień porty w konfiguracji
```

#### 4. Za mało pamięci RAM
```bash
# Błąd: "Java heap space" lub system działa wolno
```
**Rozwiązanie:** Zmniejsz zużycie pamięci:
```bash
# Edytuj .env:
SPARK_MASTER_URL=local[1]  # tylko 1 rdzeń
ORDERS_PER_SECOND=1        # mniej zamówień
```

#### 5. Niekompatybilna wersja Java
```bash
# Błąd: "Unsupported major.minor version"
```
**Rozwiązanie:** Zainstaluj Java 11:
```bash
# Ubuntu/Debian
sudo apt install openjdk-11-jdk

# Ustaw domyślną wersję
sudo update-alternatives --config java
```

## 🔄 Reinstalacja

Jeśli instalacja się nie powiodła, możesz wszystko wyczyścić i zainstalować ponownie:

```bash
# Zatrzymaj wszystkie procesy
./stop.sh

# Wyczyść pobrane komponenty
rm -rf kafka_2.13-3.6.0
rm -rf spark-3.5.0-bin-hadoop3  
rm -rf venv
rm -rf logs
rm -rf pids

# Zainstaluj ponownie
./install.sh
```

## 📱 Instalacja na różnych systemach

### Ubuntu 20.04/22.04 LTS
```bash
# Aktualizuj system
sudo apt update && sudo apt upgrade -y

# Sklonuj i zainstaluj
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED
./quickstart.sh
```

### CentOS 8/RHEL 8/Fedora
```bash
# Aktualizuj system
sudo dnf update -y

# Sklonuj i zainstaluj
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED
./quickstart.sh
```

### macOS (z Homebrew)
```bash
# Zainstaluj Homebrew jeśli nie masz
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Sklonuj i zainstaluj
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED
./quickstart.sh
```

### Arch Linux
```bash
# Zainstaluj git jeśli nie masz
sudo pacman -S git

# Sklonuj i zainstaluj
git clone https://github.com/NatanTulo/ASEED.git
cd ASEED
./quickstart.sh
```

## 🏢 Instalacja w środowisku korporacyjnym

### Za proxy/firewall
```bash
# Skonfiguruj proxy przed instalacją
export http_proxy=http://proxy.company.com:8080
export https_proxy=https://proxy.company.com:8080
export no_proxy=localhost,127.0.0.1

# Następnie normalnie
./quickstart.sh
```

### Bez uprawnień sudo
Jeśli nie masz uprawnień sudo, musisz ręcznie zainstalować:
1. Java 11+ (poproś administratora)
2. Python 3.8+ (można przez pyenv)
3. Narzędzia: wget, curl, tar

Następnie:
```bash
# Pomiń sprawdzenie wymagań systemowych
./install.sh --skip-system-packages
```

### W środowisku izolowanym (air-gapped)
1. Pobierz na maszynie z internetem:
   - `kafka_2.13-3.6.0.tgz`
   - `spark-3.5.0-bin-hadoop3.tgz`
   - Pakiety Python (pip download)

2. Przenieś na docelową maszynę i wypakuj ręcznie

3. Utwórz środowisko Python i zainstaluj pakiety offline

## ✅ Weryfikacja sukcesu instalacji

Po instalacji powinieneś zobaczyć:

```bash
make status
# ✅ Zookeeper: DZIAŁA (PID: xxxx)
# ✅ Kafka: DZIAŁA (PID: xxxx)
# ✅ Order Simulator: DZIAŁA (PID: xxxx)
# ✅ Data Analyzer: DZIAŁA (PID: xxxx)
```

I aktywne logi:
```bash
tail -f logs/data_analyzer.log
# TOP PRODUKTY - Batch 1
# 1. Electronics Smart Watch 15
#    Kategoria: Electronics
#    Zamówienia: 3, Ilość: 8
```

## 📞 Wsparcie

Jeśli nadal masz problemy z instalacją:

1. Przeczytaj [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Sprawdź logi: `ls -la logs/`
3. Uruchom debugowanie: `bash -x install.sh`
4. Sprawdź wymagania: `./check-requirements.sh`

Najczęstsze problemy to:
- Za mało pamięci RAM (< 4GB)
- Zajęte porty 2181/9092
- Brak internetu podczas instalacji
- Niekompatybilna wersja Java
