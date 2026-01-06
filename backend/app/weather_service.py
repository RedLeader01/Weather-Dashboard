"""Időjárás szolgáltatás - Külső API integráció"""
import requests
import logging
from typing import Optional, Dict, Any
from .config import settings

logger = logging.getLogger(__name__)

class WeatherService:
    """Időjárás API szolgáltatás"""
    
    @staticmethod
    def kelvin_to_celsius(kelvin: float) -> float:
        """Kelvin átváltása Celsiusra - tiszta függvény"""
        return round(kelvin - 273.15, 1)
    
    @staticmethod
    def degrees_to_direction(degrees: int) -> str:
        """Fokok átváltása szélirányra"""
        directions = ["Észak", "Észak-ÉK", "ÉK", "DK", "Dél", "DNy", "Ny", "ÉNy"]
        index = round(degrees / 45) % 8
        return directions[index]
    
    def get_weather_by_city(self, city: str) -> Optional[Dict[str, Any]]:
        """Időjárás lekérdezése OpenWeatherMap API-ról"""
        try:
            url = f"{settings.OPENWEATHER_BASE_URL}/weather"
            params = {
                "q": city,
                "appid": settings.OPENWEATHER_API_KEY,
                "lang": "hu"
            }
            
            logger.info(f"Fetching weather for {city}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Adatok feldolgozása
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": self.kelvin_to_celsius(data["main"]["temp"]),
                "feels_like": self.kelvin_to_celsius(data["main"]["feels_like"]),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": self.degrees_to_direction(data["wind"].get("deg", 0)),
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"]
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather for {city}: {e}")
            return None
        except KeyError as e:
            logger.error(f"Invalid response format for {city}: {e}")
            return None
    
    def get_weather_for_multiple_cities(self, cities: list) -> Dict[str, Any]:
        """Több város időjárásának lekérése"""
        results = {}
        for city in cities:
            weather = self.get_weather_by_city(city)
            if weather:
                results[city] = weather
        
        return results