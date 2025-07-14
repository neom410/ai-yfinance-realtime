#!/usr/bin/env python3
"""
Setup script per AI Financial Analysis Platform
Automatizza l'installazione e configurazione del progetto
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_step(step_num, title, description=""):
    """Stampa intestazione step"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    if description:
        print(f"{description}")
    print('='*60)

def run_command(command, check=True, capture_output=False):
    """Esegue comando shell"""
    print(f"Eseguendo: {command}")
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=check)
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore nell'esecuzione: {e}")
        return False

def check_python_version():
    """Controlla versione Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ richiesto")
        print(f"Versione attuale: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_git():
    """Controlla se Git è disponibile"""
    try:
        run_command("git --version", capture_output=True)
        print("✅ Git disponibile")
        return True
    except:
        print("❌ Git non trovato")
        return False

def create_virtual_environment():
    """Crea ambiente virtuale"""
    print("Creando ambiente virtuale...")
    
    if os.path.exists("venv"):
        print("⚠️  Ambiente virtuale già esistente")
        response = input("Vuoi rimuovere e ricreare? (y/N): ")
        if response.lower() == 'y':
            if sys.platform == "win32":
                run_command("rmdir /s venv")
            else:
                run_command("rm -rf venv")
        else:
            return True
    
    success = run_command(f"{sys.executable} -m venv venv")
    if success:
        print("✅ Ambiente virtuale creato")
        return True
    else:
        print("❌ Errore nella creazione ambiente virtuale")
        return False

def activate_and_install_requirements():
    """Attiva ambiente e installa dipendenze"""
    print("Installando dipendenze...")
    
    # Percorso per l'attivazione
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Aggiorna pip
    success = run_command(f"{pip_cmd} install --upgrade pip")
    if not success:
        return False
    
    # Installa requirements
    if os.path.exists("requirements.txt"):
        success = run_command(f"{pip_cmd} install -r requirements.txt")
        if success:
            print("✅ Dipendenze installate")
            return True
        else:
            print("❌ Errore nell'installazione dipendenze")
            return False
    else:
        print("❌ File requirements.txt non trovato")
        return False

def setup_environment_file():
    """Configura file .env"""
    print("Configurando file di ambiente...")
    
    if os.path.exists(".env"):
        print("⚠️  File .env già esistente")
        return True
    
    if os.path.exists(".env.example"):
        # Copia .env.example a .env
        if sys.platform == "win32":
            run_command("copy .env.example .env")
        else:
            run_command("cp .env.example .env")
        
        print("✅ File .env creato da template")
        print("⚠️  IMPORTANTE: Configura le API keys nel file .env")
        
        # Chiedi se vuole configurare ora
        response = input("Vuoi configurare le API keys ora? (y/N): ")
        if response.lower() == 'y':
            configure_api_keys()
        
        return True
    else:
        print("❌ File .env.example non trovato")
        return False

def configure_api_keys():
    """Configura API keys interattivamente"""
    print("\nConfigurazione API Keys:")
    print("Per utilizzare tutte le funzionalità, hai bisogno di:")
    print("1. OpenAI API Key (obbligatoria per AI analysis)")
    print("2. Alpha Vantage API Key (opzionale)")
    
    # Leggi file .env esistente
    env_content = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_content[key] = value
    
    # OpenAI API Key
    openai_key = input("\nInserisci OpenAI API Key (sk-...): ").strip()
    if openai_key:
        env_content["OPENAI_API_KEY"] = openai_key
    
    # Alpha Vantage API Key
    av_key = input("Inserisci Alpha Vantage API Key (opzionale): ").strip()
    if av_key:
        env_content["ALPHA_VANTAGE_API_KEY"] = av_key
    
    # Scrivi file .env aggiornato
    with open(".env", "w") as f:
        f.write("# AI Financial Analysis Platform - Environment Variables\n\n")
        for key, value in env_content.items():
            f.write(f"{key}={value}\n")
    
    print("✅ API keys configurate")

def create_project_structure():
    """Crea struttura cartelle se non esiste"""
    print("Verificando struttura del progetto...")
    
    required_dirs = [
        "src",
        "src/data",
        "src/ai", 
        "src/api",
        "src/utils",
        "tests",
        "docs",
        "logs",
        "backups"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✅ Creata cartella: {dir_path}")
        
        # Crea __init__.py per i pacchetti Python
        if dir_path.startswith("src/"):
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    f.write(f'"""Modulo {dir_path.replace("/", ".")}"""\n')

def run_tests():
    """Esegue test di base"""
    print("Eseguendo test di base...")
    
    if not os.path.exists("tests/test_basic.py"):
        print("⚠️  File di test non trovato, saltando...")
        return True
    
    # Usa Python dell'ambiente virtuale
    if sys.platform == "win32":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    success = run_command(f"{python_cmd} -m pytest tests/test_basic.py -v")
    
    if success:
        print("✅ Test completati con successo")
        return True
    else:
        print("⚠️  Alcuni test sono falliti (normale se non hai API keys)")
        return True  # Non blocchiamo per test falliti

def create_launch_scripts():
    """Crea script per lanciare l'applicazione"""
    print("Creando script di lancio...")
    
    # Script per Windows
    windows_script = """@echo off
echo Avviando AI Financial Analysis Platform...
call venv\\Scripts\\activate
streamlit run main.py
pause
"""
    
    with open("start_windows.bat", "w") as f:
        f.write(windows_script)
    
    # Script per Unix/Linux/macOS
    unix_script = """#!/bin/bash
echo "Avviando AI Financial Analysis Platform..."
source venv/bin/activate
streamlit run main.py
"""
    
    with open("start_unix.sh", "w") as f:
        f.write(unix_script)
    
    # Rendi eseguibile su Unix
    if sys.platform != "win32":
        run_command("chmod +x start_unix.sh")
    
    print("✅ Script di lancio creati")

def check_api_connectivity():
    """Controlla connettività API (opzionale)"""
    print("Verificando connettività...")
    
    try:
        # Test connessione internet
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✅ Connessione internet OK")
        
        # Test yfinance
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        if info:
            print("✅ yfinance funzionante")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Problemi di connettività: {e}")
        return False

def create_sample_config():
    """Crea configurazione di esempio"""
    print("Creando configurazione di esempio...")
    
    sample_config = {
        "default_symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
        "analysis_settings": {
            "default_period": "3mo",
            "default_interval": "1d",
            "enable_predictions": True,
            "enable_signals": True,
            "enable_sentiment": True,
            "enable_patterns": False
        },
        "ui_settings": {
            "theme": "light",
            "page_width": "wide",
            "show_advanced_metrics": False
        },
        "performance": {
            "cache_timeout": 300,
            "max_concurrent_requests": 5
        }
    }
    
    with open("config_sample.json", "w") as f:
        json.dump(sample_config, f, indent=2)
    
    print("✅ Configurazione di esempio creata (config_sample.json)")

def show_next_steps():
    """Mostra i prossimi passi"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETATO!")
    print("="*60)
    
    print("\n📋 PROSSIMI PASSI:")
    print("\n1. 🔑 Configura le API keys:")
    print("   - Ottieni OpenAI API key da: https://platform.openai.com/api-keys")
    print("   - Modifica il file .env con le tue chiavi")
    
    print("\n2. 🚀 Avvia l'applicazione:")
    if sys.platform == "win32":
        print("   - Windows: Doppio click su start_windows.bat")
        print("   - Oppure: start_windows.bat")
    else:
        print("   - Unix/Linux/macOS: ./start_unix.sh")
    print("   - Manuale: streamlit run main.py")
    
    print("\n3. 🌐 Accedi all'applicazione:")
    print("   - Apri browser su: http://localhost:8501")
    
    print("\n4. 📚 Documentazione:")
    print("   - Leggi README.md per dettagli")
    print("   - Esempi in docs/")
    
    print("\n5. 🔧 Personalizzazione:")
    print("   - Modifica config_sample.json per le tue preferenze")
    print("   - Aggiungi i tuoi simboli preferiti nella sidebar")
    
    print("\n⚠️  IMPORTANTE:")
    print("   - Senza OpenAI API key, l'analisi AI non funzionerà")
    print("   - I dati sono solo per scopi educativi")
    print("   - Non costituisce consulenza finanziaria")

def main():
    """Funzione principale del setup"""
    print("🤖 AI Financial Analysis Platform - Setup")
    print("Configurazione automatica del progetto\n")
    
    # Step 1: Verifica prerequisiti
    print_step(1, "Verifica Prerequisiti")
    
    if not check_python_version():
        print("❌ Setup interrotto: Python 3.8+ richiesto")
        return False
    
    check_git()  # Non bloccante
    
    # Step 2: Struttura progetto
    print_step(2, "Creazione Struttura Progetto")
    create_project_structure()
    
    # Step 3: Ambiente virtuale
    print_step(3, "Ambiente Virtuale", "Creazione e configurazione ambiente isolato")
    
    if not create_virtual_environment():
        print("❌ Setup interrotto: impossibile creare ambiente virtuale")
        return False
    
    # Step 4: Dipendenze
    print_step(4, "Installazione Dipendenze", "Download e installazione pacchetti Python")
    
    if not activate_and_install_requirements():
        print("❌ Setup interrotto: impossibile installare dipendenze")
        return False
    
    # Step 5: Configurazione ambiente
    print_step(5, "Configurazione Ambiente", "Setup file .env e variabili")
    
    if not setup_environment_file():
        print("⚠️  Problema con configurazione ambiente, continuando...")
    
    # Step 6: Test
    print_step(6, "Test di Base", "Verifica funzionamento componenti")
    run_tests()  # Non bloccante
    
    # Step 7: Script di lancio
    print_step(7, "Script di Lancio", "Creazione shortcut per avvio applicazione")
    create_launch_scripts()
    
    # Step 8: Configurazione
    print_step(8, "Configurazione", "File di configurazione e esempi")
    create_sample_config()
    
    # Step 9: Test connettività
    print_step(9, "Test Connettività", "Verifica accesso servizi esterni")
    check_api_connectivity()  # Non bloccante
    
    # Finale
    show_next_steps()
    
    return True

def quick_start():
    """Setup rapido per utenti esperti"""
    print("🚀 QUICK SETUP")
    
    commands = [
        f"{sys.executable} -m venv venv",
        "venv/bin/pip install -r requirements.txt" if sys.platform != "win32" else "venv\\Scripts\\pip install -r requirements.txt",
        "cp .env.example .env" if sys.platform != "win32" else "copy .env.example .env"
    ]
    
    for cmd in commands:
        run_command(cmd)
    
    print("✅ Setup rapido completato!")
    print("⚠️  Ricordati di configurare .env con le API keys")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_start()
    else:
        try:
            success = main()
            if success:
                print("\n🎉 Setup completato con successo!")
            else:
                print("\n❌ Setup fallito")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n⚠️  Setup interrotto dall'utente")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Errore durante setup: {e}")
            sys.exit(1)
