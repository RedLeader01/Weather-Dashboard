"""Konfiguráció kezelés környezeti változókkal"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Adatbázis konfiguráció
    DATABASE_URL: str = "sqlite:///./weather.db"
    
    # API konfiguráció
    OPENWEATHER_API_KEY: str
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    
    # Alkalmazás konfiguráció
    APP_NAME: str = "Weather Dashboard API"
    VERSION: str = "1.0.0"
    
    # Automatizálás
    SCHEDULE_INTERVAL_MINUTES: int = 30
    DEFAULT_CITIES: list = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr"]
    
    class Config:
        env_file = ".env"

settings = Settings()