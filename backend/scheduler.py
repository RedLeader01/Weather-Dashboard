"""
⏰ Időzített feladatok - Automatizálás külön fájlban
"""
import schedule
import threading
import time
from datetime import datetime
from sqlalchemy.orm import Session

# Relatív importok
from .config import config
from .main import (
    get_db,  # Adatbázis session
    fetch_weather_from_api,  # API hívás
    save_weather_to_db,  # Adat mentés
)

class WeatherScheduler:
    """Időjárás adatgyűjtő scheduler"""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        
    def update_weather_for_city(self, city: str):
        """Időjárás frissítése egy városra"""
        print(f"[Scheduler] Frissítés: {city}")
        
        # API hívás
        weather_data = fetch_weather_from_api(city)
        if not weather_data:
            print(f"  ❌ Hiba: {city} adatai nem érhetők el")
            return False
        
        # Adatbázis mentés
        try:
            db = next(get_db())
            save_weather_to_db(db, weather_data)
            print(f"  ✅ {city} adatai mentve")
            return True
        except Exception as e:
            print(f"  ❌ Hiba mentéskor: {e}")
            return False
    
    def scheduled_update(self):
        """Időzített frissítés az összes városra"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚀 Automatikus adatgyűjtés indult")
        
        success_count = 0
        for city in config.DEFAULT_CITIES:
            if self.update_weather_for_city(city):
                success_count += 1
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Adatgyűjtés kész: {success_count}/{len(config.DEFAULT_CITIES)} város")
    
    def start(self):
        """Scheduler indítása"""
        if self.is_running:
            print("⚠️  Scheduler már fut")
            return
        
        self.is_running = True
        
        # Azonnali frissítés indításkor
        print("🚀 Scheduler indítása...")
        self.scheduled_update()
        
        # Ütemezés beállítása
        interval = config.SCHEDULE_INTERVAL
        schedule.every(interval).minutes.do(self.scheduled_update)
        
        print(f"✅ Scheduler elindítva, frissítés {interval} percenként")
        
        # Scheduler futtatása külön szálon
        def run():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 1 percenként ellenőriz
        
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Scheduler leállítása"""
        if not self.is_running:
            return
        
        self.is_running = False
        schedule.clear()
        
        if self.thread:
            self.thread.join(timeout=2)
        
        print("🛑 Scheduler leállítva")
    
    def manual_refresh(self):
        """Manuális frissítés"""
        print("🔃 Manuális frissítés kérés...")
        self.scheduled_update()

# Globális scheduler példány
scheduler = WeatherScheduler()