"""
🌤️ Weather Dashboard Backend - 7 NAPOS ELŐREJELZÉSSEL KIBŐVÍTVE
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests
import logging
from typing import List, Optional, Dict
import math

# Abszolút importok
try:
    from .config import config
    from .scheduler import WeatherScheduler 
except ImportError:
    from config import config
    from scheduler import WeatherScheduler

# 1. Logging beállítás
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 2. Adatbázis beállítás
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Adatmodell
class WeatherRecord(Base):
    """Időjárás rekord modell"""
    __tablename__ = "weather"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    temperature = Column(Float)
    humidity = Column(Integer)
    pressure = Column(Integer, nullable=True)
    wind_speed = Column(Float, nullable=True)
    description = Column(String)
    icon = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Tábla létrehozása
Base.metadata.create_all(bind=engine)

# 4. Pydantic modellek
class WeatherResponse(BaseModel):
    """API válasz séma"""
    city: str
    temperature: float
    humidity: int
    pressure: Optional[int] = None
    wind_speed: Optional[float] = None
    description: str
    icon: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class WeatherStats(BaseModel):
    """Statisztika séma"""
    city: str
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    avg_humidity: float
    record_count: int
    last_update: Optional[datetime] = None

class DailyForecast(BaseModel):
    """Napi előrejelzés séma"""
    date: str
    day_temp: float
    night_temp: float
    min_temp: float
    max_temp: float
    humidity: int
    pressure: int
    wind_speed: float
    description: str
    icon: str
    pop: float  # Precipitation probability - csapadék valószínűség
    
    class Config:
        from_attributes = True

class ForecastResponse(BaseModel):
    """Előrejelzés válasz séma"""
    city: str
    country: str
    forecasts: List[DailyForecast]
    last_update: datetime

# 5. Helper függvények
def kelvin_to_celsius(kelvin: float) -> float:
    """Kelvin → Celsius konverzió"""
    return round(kelvin - 273.15, 2)

def get_db():
    """Adatbázis session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def fetch_weather_from_api(city: str):
    """Időjárás lekérdezése OpenWeather API-ról"""
    try:
        logger.info(f"API hívás: {city}")
        
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": config.OPENWEATHER_API_KEY,
                "lang": "hu",
                "units": "metric"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "timestamp": datetime.utcnow()
            }
        else:
            logger.error(f"API hiba ({response.status_code}): {city}")
            
    except Exception as e:
        logger.error(f"Hiba API hívásnál ({city}): {e}")
    
    return None

def fetch_forecast_from_api(city: str):
    """7 napos előrejelzés lekérdezése OpenWeather API-ról"""
    try:
        logger.info(f"Előrejelzés API hívás: {city}")
        
        # OpenWeather 5 napos/3 órás előrejelzés
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": city,
                "appid": config.OPENWEATHER_API_KEY,
                "lang": "hu",
                "units": "metric",
                "cnt": 40  # 5 nap * 8 mérés/nap = 40
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return process_forecast_data(data)
        else:
            logger.error(f"Előrejelzés API hiba ({response.status_code}): {city}")
            
    except Exception as e:
        logger.error(f"Hiba előrejelzés API hívásnál ({city}): {e}")
    
    return None

def process_forecast_data(data: dict):
    """API adatok feldolgozása napi előrejelzésekké (7 napra)"""
    try:
        city = data["city"]["name"]
        country = data["city"]["country"]
        
        # Csoportosítás dátum szerint
        daily_data = {}
        
        for forecast in data["list"]:
            # Konvertálás UTC időből
            dt = datetime.fromtimestamp(forecast["dt"])
            date_str = dt.strftime("%Y-%m-%d")
            hour = dt.hour
            
            if date_str not in daily_data:
                daily_data[date_str] = {
                    "day_temps": [],   # 9-18 óra
                    "night_temps": [], # 21-6 óra
                    "temps": [],
                    "humidities": [],
                    "pressures": [],
                    "wind_speeds": [],
                    "descriptions": [],
                    "icons": [],
                    "pops": []
                }
            
            daily_data[date_str]["temps"].append(forecast["main"]["temp"])
            daily_data[date_str]["humidities"].append(forecast["main"]["humidity"])
            daily_data[date_str]["pressures"].append(forecast["main"]["pressure"])
            daily_data[date_str]["wind_speeds"].append(forecast["wind"]["speed"])
            daily_data[date_str]["descriptions"].append(forecast["weather"][0]["description"])
            daily_data[date_str]["icons"].append(forecast["weather"][0]["icon"])
            daily_data[date_str]["pops"].append(forecast.get("pop", 0))
            
            # Nappali/éjszakai hőmérséklet elkülönítése
            if 9 <= hour <= 18:
                daily_data[date_str]["day_temps"].append(forecast["main"]["temp"])
            elif hour <= 6 or hour >= 21:
                daily_data[date_str]["night_temps"].append(forecast["main"]["temp"])
        
        # Napi előrejelzések létrehozása
        forecasts = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Csak jövőbeli napok (ma és utána)
        future_dates = [date for date in daily_data.keys() if date >= today]
        future_dates.sort()
        
        for date_str in future_dates[:7]:  # Maximum 7 nap
            values = daily_data[date_str]
            
            # Ha nincs nappali/éjszakai adat, használjuk az átlagot
            avg_day_temp = sum(values["day_temps"])/len(values["day_temps"]) if values["day_temps"] else sum(values["temps"])/len(values["temps"])
            avg_night_temp = sum(values["night_temps"])/len(values["night_temps"]) if values["night_temps"] else sum(values["temps"])/len(values["temps"])
            
            # Leggyakorbbi leírás és ikon
            most_common_desc = max(set(values["descriptions"]), key=values["descriptions"].count)
            most_common_icon = max(set(values["icons"]), key=values["icons"].count)
            
            forecasts.append(DailyForecast(
                date=date_str,
                day_temp=round(avg_day_temp, 1),
                night_temp=round(avg_night_temp, 1),
                min_temp=round(min(values["temps"]), 1),
                max_temp=round(max(values["temps"]), 1),
                humidity=round(sum(values["humidities"])/len(values["humidities"])),
                pressure=round(sum(values["pressures"])/len(values["pressures"])),
                wind_speed=round(sum(values["wind_speeds"])/len(values["wind_speeds"]), 1),
                description=most_common_desc,
                icon=most_common_icon,
                pop=round(max(values["pops"]) * 100)  # Százalékban
            ))
        
        return ForecastResponse(
            city=city,
            country=country,
            forecasts=forecasts,
            last_update=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Hiba előrejelzés feldolgozásánál: {e}")
        return None

def save_weather_to_db(weather_data: dict):
    """Időjárás adat mentése adatbázisba"""
    db = SessionLocal()
    try:
        record = WeatherRecord(**weather_data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return True
    except Exception as e:
        logger.error(f"Hiba mentéskor: {e}")
        return False
    finally:
        db.close()

# 6. Scheduler létrehozása és konfigurálása
scheduler = WeatherScheduler(
    fetch_weather_func=fetch_weather_from_api,
    save_weather_func=save_weather_to_db
)

# 7. CRUD műveletek
def get_latest_weather(db: Session, city: str):
    """Legfrissebb időjárás adat"""
    return db.query(WeatherRecord)\
             .filter(WeatherRecord.city == city)\
             .order_by(WeatherRecord.timestamp.desc())\
             .first()

def get_weather_history(db: Session, city: str, limit: int = 10):
    """Időjárás előzmények"""
    return db.query(WeatherRecord)\
             .filter(WeatherRecord.city == city)\
             .order_by(WeatherRecord.timestamp.desc())\
             .limit(limit)\
             .all()

def get_weather_stats(db: Session, city: str, hours: int = 24):
    """Statisztikák számítása"""
    time_limit = datetime.utcnow() - timedelta(hours=hours)
    
    result = db.query(
        func.count(WeatherRecord.id).label('count'),
        func.avg(WeatherRecord.temperature).label('avg_temp'),
        func.min(WeatherRecord.temperature).label('min_temp'),
        func.max(WeatherRecord.temperature).label('max_temp'),
        func.avg(WeatherRecord.humidity).label('avg_humidity'),
        func.max(WeatherRecord.timestamp).label('last_update')
    ).filter(
        WeatherRecord.city == city,
        WeatherRecord.timestamp >= time_limit
    ).first()
    
    if not result or result.count == 0:
        return None
    
    return WeatherStats(
        city=city,
        avg_temperature=round(result.avg_temp, 1),
        min_temperature=result.min_temp,
        max_temperature=result.max_temp,
        avg_humidity=round(result.avg_humidity, 1),
        record_count=result.count,
        last_update=result.last_update
    )

def get_all_cities(db: Session):
    """Összes város listázása"""
    cities = db.query(WeatherRecord.city).distinct().all()
    return [city[0] for city in cities]

# 8. FastAPI alkalmazás
app = FastAPI(
    title="Weather Dashboard API",
    version="2.1",
    description="Időjárás adatok REST API - 7 napos előrejelzéssel"
)

# CORS beállítás
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 9. API végpontok
@app.get("/")
def root():
    """Főoldal"""
    return {
        "service": "Weather Dashboard API",
        "version": "2.1",
        "status": "running",
        "features": ["current", "history", "stats", "7-day-forecast"],
        "scheduler": "active" if scheduler.is_running else "inactive",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "weather": "/api/weather?city=Budapest",
            "history": "/api/weather/history?city=Budapest",
            "stats": "/api/weather/stats?city=Budapest",
            "forecast": "/api/forecast?city=Budapest&days=7",
            "cities": "/api/cities"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": "connected",
        "scheduler": scheduler.is_running,
        "openweather_api": "configured" if config.OPENWEATHER_API_KEY and config.OPENWEATHER_API_KEY != "your_api_key_here" else "not_configured"
    }

@app.get("/api/weather", response_model=WeatherResponse)
def get_current_weather(
    city: str = Query("Budapest", description="Város neve"),
    db: Session = Depends(get_db)
):
    """Aktuális időjárás"""
    # Ellenőrizzük, van-e friss adat
    record = get_latest_weather(db, city)
    
    # Ha nincs vagy régi (>10 perc), frissítünk
    if not record or (datetime.utcnow() - record.timestamp).seconds > 600:
        logger.info(f"Friss adat szükséges: {city}")
        weather_data = fetch_weather_from_api(city)
        
        if not weather_data:
            if record:
                return WeatherResponse.from_orm(record)
            raise HTTPException(404, f"Nem található időjárás adat: {city}")
        
        # Új rekord mentése
        save_weather_to_db(weather_data)
        # Újra lekérjük
        record = get_latest_weather(db, city)
    
    return WeatherResponse.from_orm(record)

@app.get("/api/weather/history", response_model=List[WeatherResponse])
def get_history(
    city: str = Query("Budapest"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Időjárás előzmények"""
    records = get_weather_history(db, city, limit)
    return [WeatherResponse.from_orm(record) for record in records]

@app.get("/api/weather/stats", response_model=WeatherStats)
def get_stats(
    city: str = Query("Budapest"),
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """Statisztikák"""
    stats = get_weather_stats(db, city, hours)
    if not stats:
        raise HTTPException(404, f"Nincs elég adat {city} városhoz az elmúlt {hours} órában")
    return stats

@app.get("/api/forecast", response_model=ForecastResponse)
def get_weather_forecast(
    city: str = Query("Budapest", description="Város neve"),
    days: int = Query(7, ge=1, le=7, description="Napok száma (1-7)")
):
    """7 napos időjárás előrejelzés"""
    # Ellenőrizzük az API kulcsot
    if not config.OPENWEATHER_API_KEY or config.OPENWEATHER_API_KEY == "your_api_key_here":
        raise HTTPException(500, "OpenWeather API kulcs nincs beállítva")
    
    forecast_data = fetch_forecast_from_api(city)
    
    if not forecast_data:
        raise HTTPException(404, f"Nem található előrejelzés: {city}")
    
    # Limitáljuk a napok számát
    if days < len(forecast_data.forecasts):
        forecast_data.forecasts = forecast_data.forecasts[:days]
    
    return forecast_data

@app.get("/api/cities")
def get_cities(db: Session = Depends(get_db)):
    """Összes város"""
    return {"cities": get_all_cities(db)}

@app.post("/api/refresh")
def refresh_weather():
    """Manuális frissítés"""
    scheduler.manual_refresh()
    return {"message": "Manuális frissítés elindítva"}

@app.get("/api/config")
def get_config():
    """Konfiguráció lekérdezése"""
    return {
        "schedule_interval": config.SCHEDULE_INTERVAL,
        "default_cities": config.DEFAULT_CITIES,
        "scheduler_status": "active" if scheduler.is_running else "inactive",
        "openweather_configured": config.OPENWEATHER_API_KEY != "your_api_key_here"
    }

# 10. Alkalmazás indítás/leállítás
@app.on_event("startup")
def startup_event():
    """Alkalmazás indításakor"""
    logger.info("🚀 Weather API elindul...")
    
    # Konfiguráció validálása
    if config.validate():
        logger.info("✅ Konfiguráció OK")
        
        # Scheduler indítása
        scheduler.start(config.SCHEDULE_INTERVAL)
        logger.info("⏰ Scheduler elindítva")
    else:
        logger.warning("⚠️  Alkalmazás indult, de konfiguráció hiányos")

@app.on_event("shutdown")
def shutdown_event():
    """Alkalmazás leállításakor"""
    logger.info("🛑 Alkalmazás leállítása...")
    scheduler.stop()
    logger.info("✅ Scheduler leállítva")

# 11. Futtatás
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)