"""CRUD műveletek - Procedurális és funkcionális elemek"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional
from . import models, schemas

def create_weather_data(db: Session, weather: schemas.WeatherCreate):
    """Új időjárás adat létrehozása"""
    db_weather = models.WeatherData(**weather.dict())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather

def get_weather_by_city(db: Session, city: str, limit: int = 10):
    """Időjárás adatok lekérdezése város szerint"""
    return db.query(models.WeatherData)\
             .filter(models.WeatherData.city == city)\
             .order_by(desc(models.WeatherData.timestamp))\
             .limit(limit)\
             .all()

def get_latest_weather(db: Session, city: str):
    """Legfrissebb időjárás adat"""
    return db.query(models.WeatherData)\
             .filter(models.WeatherData.city == city)\
             .order_by(desc(models.WeatherData.timestamp))\
             .first()

def get_weather_stats(db: Session, city: str, hours: int = 24):
    """Statisztikák generálása"""
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    stats = db.query(
        func.count(models.WeatherData.id).label('count'),
        func.avg(models.WeatherData.temperature).label('avg_temp'),
        func.min(models.WeatherData.temperature).label('min_temp'),
        func.max(models.WeatherData.temperature).label('max_temp'),
        func.avg(models.WeatherData.humidity).label('avg_humidity'),
        func.max(models.WeatherData.timestamp).label('last_update')
    ).filter(
        models.WeatherData.city == city,
        models.WeatherData.timestamp >= time_threshold
    ).first()
    
    if stats.count == 0:
        return None
    
    return schemas.WeatherStats(
        city=city,
        avg_temperature=round(stats.avg_temp, 1),
        min_temperature=stats.min_temp,
        max_temperature=stats.max_temp,
        avg_humidity=round(stats.avg_humidity, 1),
        record_count=stats.count,
        last_update=stats.last_update
    )

def get_all_cities(db: Session):
    """Összes város lekérdezése"""
    cities = db.query(models.WeatherData.city)\
               .distinct()\
               .all()
    return [city[0] for city in cities]

def get_multi_city_weather(db: Session, cities: List[str]):
    """Több város időjárása egy API hívással"""
    result = []
    for city in cities:
        weather = get_latest_weather(db, city)
        if weather:
            result.append(weather)
    return result