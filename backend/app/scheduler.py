"""Időzített feladatok - Automatizálás"""
import schedule
import time
import threading
import logging
from datetime import datetime
from .database import SessionLocal
from .weather_service import WeatherService
from .crud import create_weather_data
from .schemas import WeatherCreate
from .config import settings

logger = logging.getLogger(__name__)

class WeatherScheduler:
    """Időzített időjárás adatgyűjtés"""
    
    def __init__(self):
        self.service = WeatherService()
        self.running = False
        
    def fetch_and_store_weather(self):
        """Időjárás adatok lekérése és tárolása"""
        logger.info(f"Starting scheduled weather fetch at {datetime.now()}")
        
        db = SessionLocal()
        try:
            for city in settings.DEFAULT_CITIES:
                weather_data = self.service.get_weather_by_city(city)
                if weather_data:
                    # Átváltás a sémához
                    weather_create = WeatherCreate(
                        city=weather_data["city"],
                        country=weather_data["country"],
                        temperature=weather_data["temperature"],
                        feels_like=weather_data.get("feels_like"),
                        humidity=weather_data["humidity"],
                        pressure=weather_data["pressure"],
                        wind_speed=weather_data["wind_speed"],
                        wind_direction=weather_data.get("wind_direction"),
                        description=weather_data["description"],
                        icon=weather_data.get("icon")
                    )
                    
                    create_weather_data(db, weather_create)
                    logger.info(f"Weather data stored for {city}")
            
            logger.info(f"Finished scheduled fetch at {datetime.now()}")
            
        except Exception as e:
            logger.error(f"Error in scheduled task: {e}")
        finally:
            db.close()
    
    def start(self, interval_minutes: int = 30):
        """Ütemező indítása"""
        self.running = True
        
        # Azonnali futás
        self.fetch_and_store_weather()
        
        # Ütemezés
        schedule.every(interval_minutes).minutes.do(self.fetch_and_store_weather)
        
        logger.info(f"Scheduler started with {interval_minutes} minute interval")
        
        # Ütemező futtatása külön szálon
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Minden percben ellenőrzés
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
    
    def stop(self):
        """Ütemező leállítása"""
        self.running = False
        logger.info("Scheduler stopped")

# Globális scheduler példány
scheduler = WeatherScheduler()