"""
🚀 Weather Dashboard indító script 
"""
import subprocess
import sys
import os
import time
import webbrowser

def run_command(command, cwd=None, wait=True):
    """Parancs futtatása"""
    print(f"▶️  {command}")
    
    if wait:
        process = subprocess.run(
            command,
            shell=True,
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
            shell=True,
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
        print("✅ Python könyvtárak OK")
        return True
    except ImportError:
        return False

def setup_environment():
    """Környezet beállítása"""
    print("\n🔧 Környezet beállítása...")
    
    # .env fájl ellenőrzése
    if not os.path.exists(".env"):
        print("📝 .env fájl létrehozása...")
        with open(".env", "w", encoding="utf-8") as f:
            f.write("""# Weather Dashboard Konfiguráció

# OpenWeather API kulcs (kötelező)
OPENWEATHER_API_KEY=your_api_key_here

# Adatbázis
DATABASE_URL=sqlite:///./weather.db

# Automatikus frissítés (percek)
SCHEDULE_INTERVAL=30

# Alapértelmezett városok
DEFAULT_CITIES=Budapest,Debrecen,Szeged,Pécs,Győr,Miskolc,Nyíregyháza

# Backend URL
BACKEND_URL=http://localhost:8000
""")
        print("⚠️  Kérlek szerkeszd a .env fájlt és add hozzá az API kulcsodat!")
        print(f"   Fájl helye: {os.path.join(os.getcwd(), '.env')}")
        return False
    
    return True

def start_backend():
    """Backend indítása"""
    print("\n🚀 Backend indítása...")
    
    # Függőségek telepítése
    print("📦 Függőségek telepítése...")
    run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    # Backend indítása
    backend_cmd = f"{sys.executable} -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    backend_process = run_command(backend_cmd, cwd="backend", wait=False)
    
    # Várunk, hogy elinduljon
    print("⏳ Backend indítása...")
    time.sleep(5)
    
    # Ellenőrizzük
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend elindult: http://localhost:8000")
            print("📚 API dokumentáció: http://localhost:8000/docs")
            return backend_process
        else:
            print("⚠️  Backend indult, de health check nem sikerült")
            return backend_process
    except:
        print("⚠️  Backend indítva, de nem lehet ellenőrizni")
        return backend_process

def start_frontend():
    """Frontend indítása"""
    print("\n🌐 Frontend indítása...")
    
    # Frontend indítása
    frontend_cmd = f"{sys.executable} -m streamlit run app.py --server.port 8501"
    frontend_process = run_command(frontend_cmd, cwd="frontend", wait=False)
    
    time.sleep(3)
    print("✅ Frontend elindult: http://localhost:8501")
    
        
    return frontend_process
def display_ascii_art():
    """ASCII art megjelenítése"""
    print(r"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🌤️  WEATHER DASHBOARD v2.2 - MODULÁRIS VERZIÓ   🌤️    ║
    ║                                                          ║
    ║            Mikroszerviz architektúra Pythonban           ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
def main():
    """Fő függvény"""
    display_ascii_art()
    
    # Ellenőrzések
    if not check_dependencies():
        print("\n📦 Függőségek telepítése...")
        run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    if not setup_environment():
        print("\n⚠️  Folytatás a hiányos konfigurációval...")
        time.sleep(2)
    
    # Alkalmazások indítása
    processes = []
    
    try:
        # Backend indítása
        backend = start_backend()
        if backend:
            processes.append(backend)
        
        # Frontend indítása
        frontend = start_frontend()
        if frontend:
            processes.append(frontend)
        
        # Információk
        print("\n" + "=" * 60)
        print("✅ ALKALMAZÁS ELINDULT!")
        print("=" * 60)
        print("\n🌐 Frontend:     http://localhost:8501")
        print("⚡ Backend API:  http://localhost:8000")
        print("📚 Dokumentáció: http://localhost:8000/docs")
        print("\n⏸️  Nyomj CTRL+C-t a leállításhoz...")
        print("=" * 60)
        
        # Várakozás a processzekre
        for process in processes:
            if process:
                process.wait()
                
    except KeyboardInterrupt:
        print("\n\n🛑 Alkalmazás leállítása...")
    except Exception as e:
        print(f"\n❌ Hiba történt: {e}")
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

if __name__ == "__main__":
    main()