"""
🚀 Weather Dashboard indító script
Könnyű használat - egy kattintás
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
            text=True
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
            text=True
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
        print("❌ Hiányzó könyvtárak")
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
DEFAULT_CITIES=Budapest,Debrecen,Szeged,Pécs,Győr
""")
        print("⚠️  Kérlek szerkeszd a .env fájlt és add hozzá az API kulcsodat!")
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

def start_backend():
    """Backend indítása"""
    print("\n🚀 Backend indítása...")
    
    # Függőségek telepítése
    print("📦 Függőségek telepítése...")
    run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    # Backend indítása
    backend_cmd = f"{sys.executable} -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
    backend_process = run_command(backend_cmd, wait=False)
    
    # Várunk, hogy elinduljon
    time.sleep(5)
    print("✅ Backend elindult: http://localhost:8000")
    
    return backend_process

def start_frontend():
    """Frontend indítása"""
    print("\n🌐 Frontend indítása...")
    
    # Frontend indítása
    frontend_cmd = f"{sys.executable} -m streamlit run frontend/app.py"
    frontend_process = run_command(frontend_cmd, wait=False)
    
    time.sleep(3)
    print("✅ Frontend elindult: http://localhost:8501")
    
    # Böngésző megnyitása
    webbrowser.open("http://localhost:8501")
    
    return frontend_process

def main():
    """Fő függvény"""
    print("=" * 50)
    print("🌤️  WEATHER DASHBOARD INDÍTÓ")
    print("=" * 50)
    
    # Ellenőrzések
    if not check_dependencies():
        print("\n📦 Függőségek telepítése...")
        run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    if not setup_environment():
        print("\n⛔ Kilépés...")
        return
    
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
        print("\n" + "=" * 50)
        print("✅ ALKALMAZÁS ELINDULT!")
        print("=" * 50)
        print("\n🌐 Frontend: http://localhost:8501")
        print("⚡ Backend API: http://localhost:8000")
        print("📚 API dokumentáció: http://localhost:8000/docs")
        print("\n⏸️  Nyomj CTRL+C-t a leállításhoz...")
        print("=" * 50)
        
        # Várakozás a processzekre
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n\n⛔ Alkalmazás leállítása...")
        
        for process in processes:
            if process:
                process.terminate()
        
        print("✅ Alkalmazás leállítva")
    except Exception as e:
        print(f"\n❌ Hiba történt: {e}")
        
        for process in processes:
            if process:
                process.terminate()

if __name__ == "__main__":
    main()