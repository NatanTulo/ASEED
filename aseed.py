#!/usr/bin/env python3
"""
ASEED - Apache Spark + Kafka E-commerce Order Analytics
Główny skrypt do zarządzania systemem analizy zamówień w czasie rzeczywistym.
"""

import os
import sys
import time
import signal
import subprocess
import argparse
import json
from pathlib import Path

# Dodaj ścieżkę src do Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class ASEEDManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.pids_dir = self.project_root / 'pids'
        self.logs_dir = self.project_root / 'logs'
        self.kafka_dir = self.project_root / 'kafka_2.13-3.9.0'
        
        # Create directories if they don't exist
        self.pids_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Service configurations
        self.services = {
            'zookeeper': {
                'command': [
                    str(self.kafka_dir / 'bin' / 'zookeeper-server-start.sh'),
                    str(self.kafka_dir / 'config' / 'zookeeper.properties')
                ],
                'log_file': 'zookeeper.log',
                'wait_time': 5
            },
            'kafka': {
                'command': [
                    str(self.kafka_dir / 'bin' / 'kafka-server-start.sh'),
                    str(self.kafka_dir / 'config' / 'server.properties')
                ],
                'log_file': 'kafka.log',
                'wait_time': 10
            },
            'order_simulator': {
                'command': ['python3', 'src/order_simulator.py'],
                'log_file': 'order_simulator.log',
                'wait_time': 2
            },
            'data_analyzer': {
                'command': ['python3', 'src/data_analyzer.py'],
                'log_file': 'data_analyzer.log',
                'wait_time': 15
            },
            'dashboard': {
                'command': ['python3', 'src/web_dashboard.py'],
                'log_file': 'dashboard.log',
                'wait_time': 3
            }
        }

    def start_service(self, service_name):
        """Uruchamia pojedynczy serwis"""
        if self.is_service_running(service_name):
            print(f"⚠️  {service_name.upper()} już działa")
            return True
            
        service = self.services[service_name]
        print(f"🚀 Uruchamianie {service_name.upper()}...")
        
        # Prepare log file
        log_path = self.logs_dir / service['log_file']
        
        try:
            with open(log_path, 'a') as log_file:
                process = subprocess.Popen(
                    service['command'],
                    cwd=self.project_root,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid
                )
            
            # Save PID
            pid_file = self.pids_dir / f"{service_name}.pid"
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            print(f"✅ {service_name.upper()} uruchomiony (PID: {process.pid})")
            time.sleep(service['wait_time'])
            return True
            
        except Exception as e:
            print(f"❌ Błąd uruchamiania {service_name}: {e}")
            return False

    def stop_service(self, service_name):
        """Zatrzymuje pojedynczy serwis"""
        pid_file = self.pids_dir / f"{service_name}.pid"
        
        if not pid_file.exists():
            print(f"⚠️  {service_name.upper()} nie działa")
            return True
            
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Kill process group
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            time.sleep(2)
            
            # Force kill if still running
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except:
                pass
                
            pid_file.unlink()
            print(f"✅ {service_name.upper()} zatrzymany")
            return True
            
        except Exception as e:
            print(f"❌ Błąd zatrzymywania {service_name}: {e}")
            pid_file.unlink(missing_ok=True)
            return False

    def is_service_running(self, service_name):
        """Sprawdza czy serwis działa"""
        pid_file = self.pids_dir / f"{service_name}.pid"
        
        if not pid_file.exists():
            return False
            
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
            
        except (OSError, ValueError):
            pid_file.unlink(missing_ok=True)
            return False

    def start_all(self):
        """Uruchamia wszystkie serwisy w odpowiedniej kolejności"""
        print("🎯 ASEED - Uruchamianie systemu analizy zamówień")
        print("=" * 50)
        
        # Sprawdź i wyczyść zajęte porty
        self._check_and_cleanup_ports()
        
        # Check if Kafka topic exists, create if not
        self.ensure_kafka_topic()
        
        services_order = ['zookeeper', 'kafka', 'order_simulator', 'data_analyzer', 'dashboard']
        
        for service in services_order:
            if not self.start_service(service):
                print(f"❌ Nie udało się uruchomić {service}")
                return False
        
        print("\n✅ 🎉 System ASEED uruchomiony pomyślnie!")
        print("\n📊 Dashboard dostępny na: http://localhost:5000")
        print("📝 Logi: tail -f logs/*.log")
        print("🛑 Zatrzymanie: python aseed.py stop")
        return True

    def _check_and_cleanup_ports(self):
        """Sprawdź i wyczyść zajęte porty"""
        ports_to_check = [2181, 9092, 5000]  # Zookeeper, Kafka, Dashboard
        
        for port in ports_to_check:
            try:
                result = subprocess.run(['lsof', '-i', f':{port}'], 
                                      capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    print(f"⚠️  Port {port} zajęty - czyszczenie...")
                    # Extract PID and kill
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            pid = line.split()[1]
                            try:
                                subprocess.run(['kill', '-9', pid], check=False)
                            except:
                                pass
                    time.sleep(1)
            except:
                pass

    def stop_all(self):
        """Zatrzymuje wszystkie serwisy"""
        print("🛑 Zatrzymywanie systemu ASEED...")
        print("=" * 30)
        
        services_order = ['dashboard', 'data_analyzer', 'order_simulator', 'kafka', 'zookeeper']
        
        for service in services_order:
            self.stop_service(service)
        
        # Force cleanup pozostałych procesów
        self._force_cleanup()
        
        print("\n✅ System ASEED zatrzymany")

    def _force_cleanup(self):
        """Wymuś czyszczenie pozostałych procesów i portów"""
        try:
            # Zabij pozostałe procesy Kafka/Zookeeper
            subprocess.run(['pkill', '-f', 'kafka'], capture_output=True, check=False)
            subprocess.run(['pkill', '-f', 'zookeeper'], capture_output=True, check=False)
            
            # Wyczyść pliki PID
            for pid_file in self.pids_dir.glob('*.pid'):
                pid_file.unlink(missing_ok=True)
                
        except Exception:
            pass

    def status(self):
        """Pokazuje status wszystkich serwisów"""
        print("📊 Status systemu ASEED")
        print("=" * 25)
        
        for service_name in self.services.keys():
            status = "🟢 DZIAŁA" if self.is_service_running(service_name) else "🔴 ZATRZYMANY"
            print(f"{service_name.upper():15} {status}")
        
        print(f"\n📂 Logi: {self.logs_dir}")
        print(f"🆔 PIDs: {self.pids_dir}")

    def ensure_kafka_topic(self):
        """Tworzy topic Kafka jeśli nie istnieje"""
        if self.is_service_running('kafka'):
            try:
                subprocess.run([
                    str(self.kafka_dir / 'bin' / 'kafka-topics.sh'),
                    '--create',
                    '--topic', 'orders',
                    '--bootstrap-server', 'localhost:9092',
                    '--partitions', '3',
                    '--replication-factor', '1'
                ], capture_output=True, check=False)
            except:
                pass

    def test_data(self, minutes=5, rate=10):
        """Generuje dane testowe"""
        print(f"🧪 Generowanie danych testowych przez {minutes} minut ({rate} zamówień/min)...")
        
        try:
            subprocess.run([
                'python3', 'src/test_data_generator.py',
                '--minutes', str(minutes),
                '--rate', str(rate)
            ], cwd=self.project_root)
        except KeyboardInterrupt:
            print("\n⚠️  Generowanie danych przerwane")

def main():
    parser = argparse.ArgumentParser(
        description='ASEED - System analizy zamówień e-commerce w czasie rzeczywistym',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python aseed.py start          # Uruchom cały system
  python aseed.py stop           # Zatrzymaj system
  python aseed.py status         # Pokaż status
  python aseed.py test --minutes 5 --rate 20  # Generuj dane testowe
        """
    )
    
    parser.add_argument('command', choices=['start', 'stop', 'status', 'test'],
                       help='Komenda do wykonania')
    parser.add_argument('--minutes', type=int, default=5,
                       help='Czas generowania danych testowych (minuty)')
    parser.add_argument('--rate', type=int, default=10,
                       help='Częstotliwość zamówień (na minutę)')
    
    args = parser.parse_args()
    manager = ASEEDManager()
    
    try:
        if args.command == 'start':
            manager.start_all()
        elif args.command == 'stop':
            manager.stop_all()
        elif args.command == 'status':
            manager.status()
        elif args.command == 'test':
            manager.test_data(args.minutes, args.rate)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operacja przerwana przez użytkownika")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Błąd: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
