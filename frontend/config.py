"""Frontend konfiguráció kezelés"""
import os
from dotenv import load_dotenv

# Betöltjük a .env fájlt a projekt gyökeréből
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

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