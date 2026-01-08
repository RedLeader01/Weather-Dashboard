"""
Egységtesztek a backend szolgáltatásokhoz
"""
import pytest
from datetime import datetime, timedelta
from backend.main import kelvin_to_celsius, get_weekday_from_date

# Parametrizált teszt a hőmérséklet konverzióhoz
@pytest.mark.parametrize("kelvin, expected_celsius", [
    (273.15, 0.0),      # 0°C
    (293.15, 20.0),     # 20°C
    (253.15, -20.0),    # -20°C
    (303.15, 30.0),     # 30°C
    (283.15, 10.0),     # 10°C
])
def test_kelvin_to_celsius(kelvin, expected_celsius):
    """Kelvin-Celsius konverzió tesztelése"""
    result = kelvin_to_celsius(kelvin)
    assert result == expected_celsius
    assert isinstance(result, float)

# Parametrizált teszt a hét napjaihoz
@pytest.mark.parametrize("date_str, expected_weekday", [
    ("2024-01-01", "Hétfő"),
    ("2024-01-02", "Kedd"),
    ("2024-01-03", "Szerda"),
    ("2024-01-04", "Csütörtök"),
    ("2024-01-05", "Péntek"),
    ("2024-01-06", "Szombat"),
    ("2024-01-07", "Vasárnap"),
])
def test_get_weekday(date_str, expected_weekday):
    """Hét napjának meghatározása"""
    from frontend.utils import get_weekday
    result = get_weekday(date_str)
    assert result == expected_weekday

def test_weather_response_model():
    """Pydantic model validáció teszt"""
    from backend.main import WeatherResponse
    from datetime import datetime
    
    # Érvényes adatok
    weather_data = {
        "city": "Budapest",
        "temperature": 22.5,
        "humidity": 65,
        "description": "napos",
        "timestamp": datetime.now()
    }
    
    response = WeatherResponse(**weather_data)
    assert response.city == "Budapest"
    assert response.temperature == 22.5
    assert response.humidity == 65
    assert isinstance(response.timestamp, datetime)

def test_database_connection():
    """Adatbázis kapcsolat teszt"""
    from backend.database import SessionLocal, engine
    
    # Ellenőrizzük, hogy létrejön-e a kapcsolat
    assert engine is not None
    
    # Session létrehozása
    db = SessionLocal()
    try:
        assert db is not None
    finally:
        db.close()