"""
🧪 Weather Dashboard tesztek
Egyszerű, de teljes értékű tesztelés
"""
import pytest
from datetime import datetime

# 1. Egyszerű függvény tesztelése (Funkcionális)
def test_kelvin_to_celsius():
    """Kelvin to Celsius konverzió teszt"""
    # Ezt a függvényt a backend/main.py-ben definiálnád
    def kelvin_to_celsius(kelvin):
        return round(kelvin - 273.15, 1)
    
    assert kelvin_to_celsius(273.15) == 0.0
    assert kelvin_to_celsius(300) == 26.9
    assert kelvin_to_celsius(0) == -273.2

# 2. Parametrizált teszt (Több eset egyben)
@pytest.mark.parametrize("input_val,expected", [
    (273.15, 0.0),
    (300, 26.9),
    (0, -273.2),
    (100, -173.2),
])
def test_kelvin_conversions_parametrized(input_val, expected):
    """Parametrizált Kelvin konverzió teszt"""
    def kelvin_to_celsius(kelvin):
        return round(kelvin - 273.15, 1)
    
    assert kelvin_to_celsius(input_val) == expected

# 3. Objektumorientált teszt (Mock adatmodellel)
class MockWeatherRecord:
    """Mock időjárás rekord osztály"""
    def __init__(self, city, temperature, timestamp):
        self.city = city
        self.temperature = temperature
        self.timestamp = timestamp

def test_weather_record_creation():
    """WeatherRecord objektum létrehozás teszt"""
    record = MockWeatherRecord(
        city="Budapest",
        temperature=22.5,
        timestamp=datetime.now()
    )
    
    assert record.city == "Budapest"
    assert record.temperature == 22.5
    assert isinstance(record.timestamp, datetime)

# 4. API válasz formátum teszt
def test_api_response_format():
    """API válasz struktúra teszt"""
    # Mock API válasz
    mock_response = {
        "city": "Budapest",
        "temperature": 22.5,
        "humidity": 65,
        "description": "felhős",
        "timestamp": "2024-01-15T14:30:00"
    }
    
    # Ellenőrizzük a kulcsokat
    required_keys = ["city", "temperature", "humidity", "description", "timestamp"]
    for key in required_keys:
        assert key in mock_response
    
    # Ellenőrizzük a típusokat
    assert isinstance(mock_response["city"], str)
    assert isinstance(mock_response["temperature"], (int, float))
    assert isinstance(mock_response["humidity"], int)

# 5. Statisztika számítás teszt
def test_statistics_calculation():
    """Statisztikai számítás teszt"""
    # Mock adatok
    temperatures = [20.0, 22.5, 18.5, 25.0, 21.5]
    
    # Procedurális számítás
    def calculate_stats(temps):
        return {
            "avg": sum(temps) / len(temps),
            "min": min(temps),
            "max": max(temps),
            "count": len(temps)
        }
    
    stats = calculate_stats(temperatures)
    
    assert stats["avg"] == 21.5
    assert stats["min"] == 18.5
    assert stats["max"] == 25.0
    assert stats["count"] == 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])