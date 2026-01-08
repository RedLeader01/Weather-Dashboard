"""
⏰ Egyszerűsített Scheduler
"""
import schedule
import threading
import time
from datetime import datetime
import logging
from sqlalchemy.orm import Session

# Abszolút importok - ne importálj semmit a main-ből!
try:
    from .config import config
except ImportError:
    from config import config

logger = logging.getLogger(__name__)

class WeatherScheduler:
    """Időzített feladatok - módosítva, nincs circular import"""
    
    def __init__(self, fetch_weather_func=None, save_weather_func=None):
        """
        Inicializálás függvényekkel
        :param fetch_weather_func: Függvény, ami város alapján lekéri az időjárást
        :param save_weather_func: Függvény, ami elmenti az adatbázisba
        """
        self.is_running = False
        self.thread = None
        self.fetch_weather = fetch_weather_func
        self.save_weather = save_weather_func
        
    def update_weather_for_city(self, city: str):
        """Időjárás frissítése egy városra"""
        if not self.fetch_weather or not self.save_weather:
            logger.warning(f"Scheduler nincs konfigurálva, nem frissítem: {city}")
            return False
            
        logger.info(f"[Scheduler] Frissítés: {city}")
        
        # API hívás a megadott függvénnyel
        weather_data = self.fetch_weather(city)
        if not weather_data:
            logger.error(f"  ❌ Hiba: {city} adatai nem érhetők el")
            return False
        
        # Adatbázis mentés a megadott függvénnyel
        try:
            success = self.save_weather(weather_data)
            if success:
                logger.info(f"  ✅ {city} adatai mentve")
                return True
            else:
                logger.error(f"  ❌ Hiba mentéskor: {city}")
                return False
        except Exception as e:
            logger.error(f"  ❌ Hiba mentéskor: {e}")
            return False
    
    def scheduled_update(self):
        """Időzített frissítés az összes városra"""
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Automatikus adatgyűjtés indult")
        
        success_count = 0
        for city in config.DEFAULT_CITIES:
            if self.update_weather_for_city(city):
                success_count += 1
        
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Adatgyűjtés kész: {success_count}/{len(config.DEFAULT_CITIES)} város")
    
    def start(self, interval_minutes: int = 30):
        """Scheduler indítása"""
        if self.is_running:
            logger.warning("⚠️  Scheduler már fut")
            return
        
        self.is_running = True
        
        # Azonnali frissítés indításkor
        logger.info("🚀 Scheduler indítása...")
        self.scheduled_update()
        
        # Ütemezés beállítása
        schedule.every(interval_minutes).minutes.do(self.scheduled_update)
        
        logger.info(f"✅ Scheduler elindítva, frissítés {interval_minutes} percenként")
        
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
        
        logger.info("🛑 Scheduler leállítva")
    
    def manual_refresh(self):
        """Manuális frissítés"""
        logger.info("🔃 Manuális frissítés kérés...")
        self.scheduled_update()

# Globális scheduler példány - NEM lesz automatikusan konfigurálva!
scheduler = WeatherScheduler()