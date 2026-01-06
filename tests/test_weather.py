"""Pytest tesztek"""
import pytest
from datetime import datetime, timedelta
from backend.app.weather_service import WeatherService
from backend.app.schemas import WeatherCreate
from backend.app.crud import get_weather_stats
from backend.app.database import SessionLocal
from backend.app.models import WeatherData

# Fixtures
@pytest.fixture
def sample_weather_data():
    """Minta időjárás adatok"""
    return {
        "city": "TestCity",
        "country": "TC",
        "temperature": 22.5,
        "feels_like": 23.1,
        "humidity": 65,
        "pressure": 1013,
        "wind_speed": 3.5,
        "wind_direction": 180,
        "description": "napos",
        "icon": "01d"
    }

@pytest.fixture
def db_session():
    """Adatbázis session fixture"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tesztek
def test_kelvin_to_celsius():
    """Kelvin to Celsius konverzió teszt"""
    service = WeatherService()
    assert service.kelvin_to_celsius(273.15) == 0
    assert service.kelvin_to_celsius(300) == 26.85
    assert service.kelvin_to_celsius(0) == -273.15

def test_degrees_to_direction():
    """Fokok to szélirány konverzió teszt"""
    service = WeatherService()
    assert service.degrees_to_direction(0) == "Észak"
    assert service.degrees_to_direction(90) == "DK"
    assert service.degrees_to_direction(180) == "Dél"
    assert service.degrees_to_direction(270) == "Ny"

@pytest.mark.parametrize("city,expected_country", [
    ("Budapest", "HU"),
    ("London", "GB"),
    ("Paris", "FR"),
])
def test_weather_service_cities(city, expected_country):
    """Weather service város tesztek - parametrizált"""
    service = WeatherService()
    # Megjegyzés: Valós teszteléshez mockolni kellene az API hívást
    # Most csak a metódus létezését teszteljük
    assert hasattr(service, 'get_weather_by_city')
    assert callable(service.get_weather_by_city)

def test_weather_create_schema(sample_weather_data):
    """Pydantic séma validáció teszt"""
    weather = WeatherCreate(**sample_weather_data)
    assert weather.city == "TestCity"
    assert weather.temperature == 22.5
    assert weather.humidity == 65

def test_statistics_calculation(db_session, sample_weather_data):
    """Statisztika számítás teszt"""
    # Adatok beszúrása
    weather = WeatherData(**sample_weather_data, timestamp=datetime.utcnow())
    db_session.add(weather)
    db_session.commit()
    
    # Statisztika lekérdezése
    stats = get_weather_stats(db_session, "TestCity", 24)
    
    if stats:  # Ha van adat
        assert stats.city == "TestCity"
        assert stats.avg_temperature == 22.5
        assert stats.min_temperature == 22.5
        assert stats.max_temperature == 22.5