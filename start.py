"""
🚀 Weather Dashboard indító script - MODULÁRIS VERZIÓHOZ JAVÍTVA
"""
import subprocess
import sys
import os
import time
import threading
import webbrowser

def run_command(command, cwd=None, wait=True, shell=True):
    """Parancs futtatása"""
    print(f"▶️  {command}")
    
    if wait:
        process = subprocess.run(
            command,
            shell=shell,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(f"⚠️  {process.stderr}")
        return process.returncode
    else:
        # Háttérben futtatás
        return subprocess.Popen(
            command,
            shell=shell,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

def check_dependencies():
    """Függőségek ellenőrzése"""
    print("🔍 Függőségek ellenőrzése...")
    
    try:
        import fastapi
        import streamlit
        import sqlalchemy
        import plotly
        print("✅ Python könyvtárak OK")
        return True
    except ImportError as e:
        print(f"❌ Hiányzó könyvtárak: {e}")
        return False

def setup_environment():
    """Környezet beállítása"""
    print("\n🔧 Környezet beállítása...")
    
    # .env fájl ellenőrzése
    if not os.path.exists(".env"):
        print("📝 .env fájl létrehozása...")
        with open(".env", "w", encoding="utf-8") as f:
            f.write("""# Weather Dashboard Konfiguráció - MODULÁRIS VERZIÓ

# Backend API URL
BACKEND_URL=http://localhost:8000

# OpenWeather API kulcs (kötelező)
# Regisztrálj: https://openweathermap.org/api
OPENWEATHER_API_KEY=your_api_key_here

# Adatbázis
DATABASE_URL=sqlite:///./weather.db

# Automatikus frissítés (percek)
SCHEDULE_INTERVAL=30

# Alapértelmezett városok
DEFAULT_CITIES=Budapest,Debrecen,Szeged,Pécs,Győr,Miskolc,Nyíregyháza
""")
        print("⚠️  Kérlek szerkeszd a .env fájlt és add hozzá az API kulcsodat!")
        print("   A fájl itt található: {}/.env".format(os.getcwd()))
        return False
    
    # API kulcs ellenőrzése
    with open(".env", "r", encoding="utf-8") as f:
        content = f.read()
        if "your_api_key_here" in content:
            print("⚠️  API kulcs nincs beállítva a .env fájlban!")
            print("   Kérlek szerkeszd a .env fájlt!")
            return False
    
    print("✅ Környezet OK")
    return True

def check_backend_health(base_url="http://localhost:8000", timeout=10):
    """Backend egészségügyi állapotának ellenőrzése"""
    import requests
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend elérhető")
                return True
        except:
            pass
        time.sleep(1)
    
    return False

def start_backend():
    """Backend indítása"""
    print("\n🚀 Backend indítása...")
    
    # Függőségek telepítése (ha szükséges)
    print("📦 Függőségek telepítése...")
    run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    # Backend indítása a backend mappából
    backend_dir = "backend" if os.path.exists("backend") else "."
    
    backend_cmd = f"{sys.executable} -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    backend_process = run_command(backend_cmd, cwd=backend_dir, wait=False)
    
    # Várunk, hogy elinduljon
    print("⏳ Backend indítása... (várakozás 5 másodpercet)")
    time.sleep(5)
    
    # Ellenőrizzük, hogy elindult-e
    if check_backend_health():
        print("✅ Backend elindult: http://localhost:8000")
        print("📚 API dokumentáció: http://localhost:8000/docs")
    else:
        print("⚠️  Backend indítása lehet, hogy nem sikerült, de folytatjuk...")
    
    return backend_process

def start_frontend():
    """Frontend indítása"""
    print("\n🌐 Frontend indítása...")
    
    # Frontend indítása a frontend mappából
    frontend_dir = "frontend" if os.path.exists("frontend") else "."
    
    # Streamlit indítása
    frontend_cmd = f"{sys.executable} -m streamlit run app.py --server.port 8501 --server.headless true"
    frontend_process = run_command(frontend_cmd, cwd=frontend_dir, wait=False)
    
    time.sleep(3)
    print("✅ Frontend elindult: http://localhost:8501")
        
    # Automatikus megnyitás böngészőben
    try:
        webbrowser.open("http://localhost:8501")
        print("🌐 Böngésző megnyitva")
    except:
        pass
    
        
    return frontend_process

def display_ascii_art():
    """ASCII art megjelenítése"""
    print(r"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🌤️  WEATHER DASHBOARD v2.2 - MODULÁRIS VERZIÓ   🌤️   ║
    ║                                                          ║
    ║            Mikroszerviz architektúra Pythonban           ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def monitor_processes(processes):
    """Processzek monitorozása"""
    print("\n👁️  Alkalmazások monitorozása...")
    print("   (Nyomj CTRL+C-t a leállításhoz)")
    
    try:
        while True:
            time.sleep(5)
            # Ellenőrizzük, hogy a processzek még futnak-e
            for i, process in enumerate(processes):
                if process and process.poll() is not None:
                    print(f"⚠️  Process {i+1} leállt")
                    return False
    except KeyboardInterrupt:
        return True

def main():
    """Fő függvény"""
    display_ascii_art()
    
    # Ellenőrzések
    if not check_dependencies():
        print("\n📦 Függőségek telepítése...")
        result = run_command(f"{sys.executable} -m pip install -r requirements.txt")
        if result != 0:
            print("❌ Függőségek telepítése sikertelen")
            return
    
    if not setup_environment():
        print("\n⚠️  Folytatjuk az indítást, de az API kulcs hiányzik")
        print("   A frontend működni fog, de nem fog tudni időjárás adatokat lekérni")
        print("   Később szerkeszd a .env fájlt!")
        time.sleep(3)
    
    # Alkalmazások indítása
    processes = []
    
    try:
        # Backend indítása
        backend = start_backend()
        processes.append(backend)
        
        # Frontend indítása
        frontend = start_frontend()
        processes.append(frontend)
        
        # Információk
        print("\n" + "=" * 60)
        print("✅ ALKALMAZÁS ELINDULT!")
        print("=" * 60)
        print("\n📡 ELÉRHETŐ SZOLGÁLTATÁSOK:")
        print("   🌐 Frontend:     http://localhost:8501")
        print("   ⚡ Backend API:  http://localhost:8000")
        print("   📚 Dokumentáció: http://localhost:8000/docs")
        print("   🔧 API Health:   http://localhost:8000/health")
        print("\n🎯 HASZNÁLAT:")
        print("   1. Használd a frontendet az időjárás adatok megtekintéséhez")
        print("   2. Teszteld az API-t a dokumentáció oldalon")
        print("   3. Ellenőrizd a backend állapotát a health endpointon")
        print("\n⏸️  Nyomj CTRL+C-t a leállításhoz...")
        print("=" * 60)
        
        
        # Processzek monitorozása
        monitor_processes(processes)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Alkalmazás leállítása...")
    except Exception as e:
        print(f"\n❌ Hiba történt: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Processzek leállítása
        print("\n🔴 Processzek leállítása...")
        for process in processes:
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except:
                    try:
                        process.kill()
                    except:
                        pass
        
        print("✅ Alkalmazás leállítva")
        print("\n👋 Viszlát!")

if __name__ == "__main__":
    main()