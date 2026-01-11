"""Frontend konfiguráció kezelés - Streamlit Cloud kompatibilis"""
import os
import streamlit as st
from dotenv import load_dotenv

# Próbáljuk betölteni a .env fájlt lokális fejlesztéshez
try:
    load_dotenv()
except:
    pass

class FrontendConfig:
    """Frontend konfiguráció"""
    
    # Backend API URL - Streamlit Secrets vagy környezeti változó
    def _get_backend_url(self):
        # 1. Próbáljuk a Streamlit Secrets-ből
        try:
            if st.secrets and "BACKEND_URL" in st.secrets:
                return st.secrets["BACKEND_URL"]
        except:
            pass
        
        # 2. Próbáljuk a környezeti változóból
        env_url = os.getenv("BACKEND_URL")
        if env_url:
            return env_url
        
        # 3. Alapértelmezett (lokális fejlesztés)
        return "http://localhost:8000"
    
    @property
    def BACKEND_URL(self):
        return self._get_backend_url()
    
    # OpenWeather API kulcs (csak információként)
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    
    # Alapértelmezett városok
    def _get_default_cities(self):
        try:
            if st.secrets and "DEFAULT_CITIES" in st.secrets:
                cities_str = st.secrets["DEFAULT_CITIES"]
            else:
                cities_str = os.getenv("DEFAULT_CITIES", "Budapest,Debrecen,Szeged,Pécs,Győr,Miskolc,Nyíregyháza")
            
            return [city.strip() for city in cities_str.split(",")]
        except:
            return ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr", "Miskolc", "Nyíregyháza"]
    
    @property
    def DEFAULT_CITIES(self):
        return self._get_default_cities()
    
    # Alkalmazás beállítások
    APP_TITLE = "🌤️ Időjárás Dashboard"
    APP_ICON = "🌤️"
    APP_LAYOUT = "wide"

config = FrontendConfig()