"""Pydantic modellek - Validáció és serializáció"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Alap modell
class WeatherBase(BaseModel):
    city: str = Field(..., example="Budapest")
    country: Optional[str] = Field(None, example="HU")
    temperature: float = Field(..., example=22.5)
    feels_like: Optional[float] = Field(None, example=23.1)
    humidity: int = Field(..., example=65)
    pressure: int = Field(..., example=1013)
    wind_speed: float = Field(..., example=3.5)
    wind_direction: Optional[int] = Field(None, example=180)
    description: str = Field(..., example="felhős")
    icon: Optional[str] = Field(None, example="04d")

# API válasz modellek
class WeatherCreate(WeatherBase):
    pass

class WeatherResponse(WeatherBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Statisztika modell - Funkcionális programozás elemei
class WeatherStats(BaseModel):
    city: str
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    avg_humidity: float
    record_count: int
    last_update: Optional[datetime]

# Több város lekérdezéséhez
class MultiCityWeather(BaseModel):
    cities: List[WeatherResponse]
    timestamp: datetime = Field(default_factory=datetime.now)