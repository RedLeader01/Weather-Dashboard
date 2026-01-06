"""Függőségek"""
from .database import get_db
from .weather_service import WeatherService

# Szolgáltatások
weather_service = WeatherService()