.PHONY: help check install start stop monitor clean status logs dashboard

# Domyślna komenda
help:
	@echo "🚀 Online Store Order Analysis - Makefile"
	@echo "========================================="
	@echo ""
	@echo "Dostępne komendy:"
	@echo ""
	@echo "  make dashboard - Uruchom Web Dashboard (ZALECANE)"
	@echo "  make check     - Sprawdź wymagania systemu"
	@echo "  make install   - Zainstaluj wszystkie zależności"
	@echo "  make start     - Uruchom system"
	@echo "  make stop      - Zatrzymaj system"
	@echo "  make monitor   - Monitoruj system"
	@echo "  make status    - Pokaż status procesów"
	@echo "  make logs      - Pokaż ostatnie logi"
	@echo "  make clean     - Wyczyść logi i pliki tymczasowe"
	@echo "  make quickstart - Pełna instalacja + uruchomienie"
	@echo ""
	@echo "Przykłady:"
	@echo "  make install dashboard  # Zainstaluj i uruchom Web GUI"
	@echo "  make quickstart  # Szybki start dla nowych użytkowników"
	@echo "  make install start monitor  # Instaluj, uruchom i monitoruj"

# Sprawdź wymagania systemu
check:
	@echo "🔍 Sprawdzanie wymagań systemu..."
	./check-requirements.sh

# Zainstaluj wszystkie zależności
install:
	@echo "📦 Instalowanie zależności..."
	./install.sh

# Uruchom system
start:
	@echo "🚀 Uruchamianie systemu..."
	./start.sh

# Zatrzymaj system
stop:
	@echo "🛑 Zatrzymywanie systemu..."
	./stop.sh

# Monitoruj system
monitor:
	@echo "📊 Uruchamianie monitora..."
	./monitor.sh

# Pokaż status procesów
status:
	@echo "📋 Status procesów:"
	@echo ""
	@if pgrep -f "kafka.zookeeper" > /dev/null; then \
		echo "✅ Zookeeper: DZIAŁA (PID: $$(pgrep -f 'kafka.zookeeper'))"; \
	else \
		echo "❌ Zookeeper: NIE DZIAŁA"; \
	fi
	@if pgrep -f "kafka.Kafka" > /dev/null; then \
		echo "✅ Kafka: DZIAŁA (PID: $$(pgrep -f 'kafka.Kafka'))"; \
	else \
		echo "❌ Kafka: NIE DZIAŁA"; \
	fi
	@if pgrep -f "order_simulator.py" > /dev/null; then \
		echo "✅ Order Simulator: DZIAŁA (PID: $$(pgrep -f 'order_simulator.py'))"; \
	else \
		echo "❌ Order Simulator: NIE DZIAŁA"; \
	fi
	@if pgrep -f "data_analyzer.py" > /dev/null; then \
		echo "✅ Data Analyzer: DZIAŁA (PID: $$(pgrep -f 'data_analyzer.py'))"; \
	else \
		echo "❌ Data Analyzer: NIE DZIAŁA"; \
	fi

# Pokaż ostatnie logi
logs:
	@echo "📋 Ostatnie logi systemowe:"
	@echo ""
	@if [ -f "logs/data_analyzer.log" ]; then \
		echo "=== Data Analyzer (ostatnie 10 linii) ==="; \
		tail -n 10 logs/data_analyzer.log; \
		echo ""; \
	fi
	@if [ -f "logs/order_simulator.log" ]; then \
		echo "=== Order Simulator (ostatnie 10 linii) ==="; \
		tail -n 10 logs/order_simulator.log; \
		echo ""; \
	fi

# Wyczyść logi i pliki tymczasowe
clean:
	@echo "🧹 Czyszczenie plików tymczasowych..."
	rm -rf logs/*
	rm -rf pids/*
	@echo "✅ Wyczyszczono logi i pliki PID"

# Szybki start - pełna instalacja i uruchomienie
quickstart:
	@echo "🚀 Szybki start systemu..."
	./quickstart.sh

# Uruchom Web Dashboard
dashboard:
	@echo "🌐 Uruchamianie Web Dashboard..."
	./start-dashboard.sh

# Restart systemu
restart: stop start
	@echo "🔄 System zrestartowany"

# Aliasy dla dashboard
web: dashboard
gui: dashboard

# Weryfikacja instalacji
verify: status
	@echo ""
	@echo "🔍 Weryfikacja instalacji:"
	@if [ -d "kafka_2.13-3.6.0" ]; then \
		echo "✅ Kafka zainstalowana"; \
	else \
		echo "❌ Kafka nie jest zainstalowana"; \
	fi
	@if [ -d "spark-3.5.0-bin-hadoop3" ]; then \
		echo "✅ Spark zainstalowany"; \
	else \
		echo "❌ Spark nie jest zainstalowany"; \
	fi
	@if [ -d "venv" ]; then \
		echo "✅ Wirtualne środowisko Python istnieje"; \
	else \
		echo "❌ Wirtualne środowisko Python nie istnieje"; \
	fi
