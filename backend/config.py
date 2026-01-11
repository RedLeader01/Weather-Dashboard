"""
🔧 Konfiguráció kezelés - Környezeti változók
"""
import os
from dotenv import load_dotenv

# .env fájl betöltése
load_dotenv()

class Config:
    """Alkalmazás konfiguráció"""
    
    # OpenWeather API
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    
    # Adatbázis
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./weather.db")
    
    # Alkalmazás beállítások
    SCHEDULE_INTERVAL = int(os.getenv("SCHEDULE_INTERVAL", 30))  # perc
    DEFAULT_CITIES = os.getenv("DEFAULT_CITIES", "Budapest,Debrecen,Szeged,Pécs,Győr,Miskolc,Nyíregyháza").split(",")
    
    # CORS beállítások
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")
    
    @classmethod
    def validate(cls):
        """Konfiguráció validálása"""
        if not cls.OPENWEATHER_API_KEY or cls.OPENWEATHER_API_KEY == "your_api_key_here":
            print("⚠️  Figyelem: OpenWeather API kulcs nincs beállítva!")
            print("   Kérlek állítsd be a .env fájlban.")
            return False
        return True

# Konfiguráció példány
config = Config()