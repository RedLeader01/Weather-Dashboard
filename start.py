"""
🚀 Egyszerű indító script a Weather Dashboardhoz
"""
import subprocess
import sys
import os
import time

def run_command(command, cwd=None):
    """Parancs futtatása"""
    print(f"▶️  Futtatás: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Kimenet kiírása
    for line in process.stdout:
        print(line.strip())
    
    process.wait()
    return process.returncode

def main():
    """Fő függvény"""
    print("=" * 50)
    print("🌤️  WEATHER DASHBOARD INDÍTÓ")
    print("=" * 50)
    
    # 1. Virtuális környezet ellenőrzése
    if not os.path.exists("venv"):
        print("1. Virtuális környezet létrehozása...")
        run_command(f"{sys.executable} -m venv venv")
    
    # 2. Függőségek telepítése
    print("\n2. Függőségek telepítése...")
    
    # Pip frissítése
    pip_cmd = "venv/Scripts/pip" if sys.platform == "win32" else "venv/bin/pip"
    run_command(f"{pip_cmd} install --upgrade pip")
    
    # Requirements telepítése
    run_command(f"{pip_cmd} install -r requirements.txt")
    
    # 3. .env fájl ellenőrzése
    if not os.path.exists(".env"):
        print("\n3. .env fájl létrehozása...")
        with open(".env", "w") as f:
            f.write("OPENWEATHER_API_KEY=your_api_key_here\n")
        print("⚠️  Kérlek add hozzá az OpenWeather API kulcsodat a .env fájlhoz!")
    
    # 4. Backend indítása
    print("\n4. Backend indítása...")
    backend_cmd = "venv/Scripts/python" if sys.platform == "win32" else "venv/bin/python"
    
    # Backend külön processben
    backend_process = subprocess.Popen(
        f"{backend_cmd} -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload",
        shell=True,
        cwd=".",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    # Várunk, hogy a backend elinduljon
    time.sleep(3)
    
    # 5. Frontend indítása
    print("\n5. Frontend indítása...")
    frontend_cmd = "venv/Scripts/streamlit" if sys.platform == "win32" else "venv/bin/streamlit"
    
    # Frontend külön processben
    frontend_process = subprocess.Popen(
        f"{frontend_cmd} run frontend/app.py",
        shell=True,
        cwd=".",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    print("\n" + "=" * 50)
    print("✅ ALKALMAZÁS ELINDULT!")
    print("=" * 50)
    print("\n🌐 Frontend: http://localhost:8501")
    print("⚡ Backend API: http://localhost:8000")
    print("📚 API dokumentáció: http://localhost:8000/docs")
    print("\n⏸️  Nyomj CTRL+C-t a leállításhoz...")
    print("=" * 50)
    
    try:
        # Várakozás a processzekre
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\n⛔ Alkalmazás leállítása...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Alkalmazás leállítva")

if __name__ == "__main__":
    main()