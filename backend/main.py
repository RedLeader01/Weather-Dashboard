"""
🌤️ Időjárás Dashboard Backend - FastAPI
Egyszerű, de teljes értékű mikroszerviz
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests
import schedule
import threading
import time
import os
from dotenv import load_dotenv
import logging

# 1. Konfiguráció betöltése
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo_key")  # Demo key teszteléshez
BASE_URL = "https://api.openweathermap.org/data/2.5"

# 2. Adatbázis beállítás
DATABASE_URL = "sqlite:///./weather.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Adatmodell (OOP)
class WeatherRecord(Base):
    """Időjárás rekord tábla"""
    __tablename__ = "weather"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    temperature = Column(Float)  # Celsius
    humidity = Column(Integer)   # %
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Tábla létrehozása
Base.metadata.create_all(bind=engine)

# 4. Pydantic modellek (validáció)
class WeatherResponse(BaseModel):
    """API válasz formátuma"""
    city: str
    temperature: float
    humidity: int
    description: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class WeatherRequest(BaseModel):
    """API kérés formátuma"""
    city: str

# 5. FastAPI alkalmazás
app = FastAPI(title="Weather API", version="1.0")

# CORS engedélyezése
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Helper függvények (Funkcionális programozás)
def kelvin_to_celsius(kelvin: float) -> float:
    """Kelvinből Celsiusba konvertálás - tiszta függvény"""
    return round(kelvin - 273.15, 1)

def get_weather_description(code: str) -> str:
    """Időjárás kód magyar leírása"""
    descriptions = {
        "01d": "tiszta nap", "01n": "tiszta éjszaka",
        "02d": "kevés felhő", "02n": "kevés felhő",
        "03d": "szétszórt felhők", "03n": "szétszórt felhők",
        "04d": "felhős", "04n": "felhős",
        "09d": "zápor", "09n": "zápor",
        "10d": "eső", "10n": "eső",
        "11d": "zivatar", "11n": "zivatar",
        "13d": "hó", "13n": "hó",
        "50d": "köd", "50n": "köd"
    }
    return descriptions.get(code, "ismeretlen")

def fetch_weather_from_api(city: str):
    """Időjárás lekérdezése OpenWeather-től"""
    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={"q": city, "appid": API_KEY, "lang": "hu"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "city": data["name"],
                "temperature": kelvin_to_celsius(data["main"]["temp"]),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"]
            }
    except Exception as e:
        print(f"Hiba API hívásnál: {e}")
    return None

# 7. Adatbázis műveletek (CRUD - Procedurális)
def save_weather_to_db(city: str, temp: float, humidity: int, desc: str):
    """Időjárás mentése adatbázisba"""
    db = SessionLocal()
    try:
        record = WeatherRecord(
            city=city,
            temperature=temp,
            humidity=humidity,
            description=desc
        )
        db.add(record)
        db.commit()
        return record
    finally:
        db.close()

def get_latest_weather(city: str):
    """Legutóbbi időjárás adat"""
    db = SessionLocal()
    try:
        return db.query(WeatherRecord)\
                 .filter(WeatherRecord.city == city)\
                 .order_by(WeatherRecord.timestamp.desc())\
                 .first()
    finally:
        db.close()

def get_weather_history(city: str, limit: int = 10):
    """Időjárás előzmények"""
    db = SessionLocal()
    try:
        return db.query(WeatherRecord)\
                 .filter(WeatherRecord.city == city)\
                 .order_by(WeatherRecord.timestamp.desc())\
                 .limit(limit)\
                 .all()
    finally:
        db.close()

def get_weather_stats(city: str, hours: int = 24):
    """Statisztikák számítása"""
    db = SessionLocal()
    try:
        time_limit = datetime.utcnow() - timedelta(hours=hours)
        
        stats = db.query(
            func.count(WeatherRecord.id).label('count'),
            func.avg(WeatherRecord.temperature).label('avg_temp'),
            func.min(WeatherRecord.temperature).label('min_temp'),
            func.max(WeatherRecord.temperature).label('max_temp')
        ).filter(
            WeatherRecord.city == city,
            WeatherRecord.timestamp >= time_limit
        ).first()
        
        if stats and stats.count > 0:
            return {
                "city": city,
                "avg_temperature": round(stats.avg_temp, 1),
                "min_temperature": stats.min_temp,
                "max_temperature": stats.max_temp,
                "record_count": stats.count
            }
    finally:
        db.close()
    return None

# 8. Időzített feladat (Automatizálás)
def scheduled_weather_update():
    """Automatikus adatgyűjtés"""
    cities = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr"]
    print(f"[{datetime.now()}] Automatikus adatgyűjtés indult...")
    
    for city in cities:
        weather = fetch_weather_from_api(city)
        if weather:
            save_weather_to_db(
                city=weather["city"],
                temp=weather["temperature"],
                humidity=weather["humidity"],
                desc=weather["description"]
            )
            print(f"  ✓ {city} adatai mentve")
    
    print(f"[{datetime.now()}] Automatikus adatgyűjtés befejezve")

def start_scheduler():
    """Ütemező indítása külön szálon"""
    # Azonnali futás
    scheduled_weather_update()
    
    # Ütemezés minden 30 percben
    schedule.every(30).minutes.do(scheduled_weather_update)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Minden percben ellenőriz
    
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    print("✅ Ütemező elindítva (30 percenként)")

# 9. API végpontok
@app.get("/")
def root():
    """Főoldal"""
    return {
        "message": "🌤️ Weather Dashboard API",
        "version": "1.0",
        "endpoints": {
            "current": "/api/weather?city=Budapest",
            "history": "/api/weather/history?city=Budapest&limit=10",
            "stats": "/api/weather/stats?city=Budapest&hours=24",
            "cities": "/api/cities"
        }
    }

@app.get("/api/weather")
def get_current_weather(city: str = Query("Budapest")):
    """Aktuális időjárás"""
    # 1. Először próbáljuk az adatbázisból
    db_record = get_latest_weather(city)
    
    # 2. Ha nincs vagy régi (>5 perces), kérjük API-ból
    if not db_record or (datetime.utcnow() - db_record.timestamp).seconds > 300:
        api_weather = fetch_weather_from_api(city)
        if api_weather:
            # Mentjük adatbázisba
            record = save_weather_to_db(
                city=api_weather["city"],
                temp=api_weather["temperature"],
                humidity=api_weather["humidity"],
                desc=api_weather["description"]
            )
            return WeatherResponse.from_orm(record)
    
    if db_record:
        return WeatherResponse.from_orm(db_record)
    
    raise HTTPException(status_code=404, detail=f"Nem található időjárás adat: {city}")

@app.get("/api/weather/history")
def get_history(city: str = Query("Budapest"), limit: int = Query(10, ge=1, le=50)):
    """Előzmények"""
    records = get_weather_history(city, limit)
    return [WeatherResponse.from_orm(record) for record in records]

@app.get("/api/weather/stats")
def get_stats(city: str = Query("Budapest"), hours: int = Query(24, ge=1, le=168)):
    """Statisztikák"""
    stats = get_weather_stats(city, hours)
    if not stats:
        raise HTTPException(status_code=404, detail="Nincs elég adat a statisztikákhoz")
    return stats

@app.get("/api/cities")
def get_cities():
    """Összes város"""
    db = SessionLocal()
    try:
        cities = db.query(WeatherRecord.city).distinct().all()
        return {"cities": [city[0] for city in cities]}
    finally:
        db.close()

@app.post("/api/weather/refresh")
def refresh_weather():
    """Manuális frissítés"""
    scheduled_weather_update()
    return {"message": "Adatok frissítve"}

# 10. Alkalmazás indítása
@app.on_event("startup")
def on_startup():
    """Alkalmazás indításakor"""
    print("🚀 Weather API elindult")
    start_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)