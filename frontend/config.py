"""Frontend konfiguráció kezelés"""
import os
from dotenv import load_dotenv
from pathlib import Path

# .env fájl betöltése
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Ha nincs .env, használjunk alapértelmezett értékeket
    print("⚠️  .env fájl nem található, alapértelmezett értékek használata")

class FrontendConfig:
    """Frontend konfiguráció"""
    
    # Backend API URL
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # OpenWeather API kulcs (csak információként)
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    
    # Alapértelmezett városok
    DEFAULT_CITIES_STR = os.getenv("DEFAULT_CITIES", "Budapest,Debrecen,Szeged,Pécs,Győr,Miskolc,Nyíregyháza")
    DEFAULT_CITIES = [city.strip() for city in DEFAULT_CITIES_STR.split(",")]
    
    # Alkalmazás beállítások
    APP_TITLE = "🌤️ Időjárás Dashboard"
    APP_ICON = "🌤️"
    APP_LAYOUT = "wide"
    
    # Stílus beállítások
    PRIMARY_COLOR = "#1E88E5"
    SECONDARY_COLOR = "#667eea"
    ACCENT_COLOR = "#764ba2"

config = FrontendConfig()