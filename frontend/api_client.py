"""API kommunikáció a backenddel"""
import requests
import streamlit as st
import time

class WeatherAPIClient:
    """Weather API kliens"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        
    def fetch_data(self, endpoint: str, params: dict = None):
        """API hívás a backendhez"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                st.warning(f"Nincs adat ehhez a lekérdezéshez")
                return None
            else:
                st.error(f"API hiba ({response.status_code}): {response.text[:100]}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Nem lehet csatlakozni az API-hoz: {self.base_url}")
            return None
        except requests.exceptions.Timeout:
            st.warning("⏰ API hívás időtúllépés, próbáld újra")
            return None
        except Exception as e:
            st.error(f"Hiba történt: {str(e)}")
            return None
    
    def get_current_weather(self, city: str):
        """Aktuális időjárás"""
        return self.fetch_data("/api/weather", {"city": city})
    
    def get_weather_history(self, city: str, limit: int = 10):
        """Időjárás előzmények"""
        return self.fetch_data("/api/weather/history", {"city": city, "limit": limit})
    
    def get_weather_stats(self, city: str, hours: int = 24):
        """Statisztikák"""
        return self.fetch_data("/api/weather/stats", {"city": city, "hours": hours})
    
    def get_weather_forecast(self, city: str, days: int = 7):
        """Előrejelzés"""
        return self.fetch_data("/api/forecast", {"city": city, "days": days})
    
    def get_all_cities(self):
        """Összes város"""
        data = self.fetch_data("/api/cities")
        return data.get('cities', []) if data else []
    
    def refresh_data(self):
        """Manuális frissítés"""
        return self.fetch_data("/api/refresh")
    
    def get_health(self):
        """Health check"""
        return self.fetch_data("/health")
    
    def test_connection(self):
        """Kapcsolat tesztelése"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=3)
            return response.status_code == 200
        except:
            return False