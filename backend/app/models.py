"""SQLAlchemy modellek - Objektumorientált programozás"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from .database import Base

class WeatherData(Base):
    """Időjárás adatok modellje"""
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    country = Column(String)
    temperature = Column(Float)  # Celsius fok
    feels_like = Column(Float)   # Hőérzet
    humidity = Column(Integer)   # Páratartalom %
    pressure = Column(Integer)   # Légnyomás hPa
    wind_speed = Column(Float)   # Szélsebesség m/s
    wind_direction = Column(Integer)  # Szélirány fokban
    description = Column(String)  # Rövid leírás
    icon = Column(String)        # Ikon kód
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Index létrehozása város és idő alapján
    __table_args__ = (
        Index('idx_city_timestamp', 'city', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<WeatherData(city={self.city}, temp={self.temperature}°C)>"