"""
🌤️ Weather Dashboard Backend - FastAPI
Egyszerűsített, scheduler külön fájlban
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
from typing import List, Optional

# Saját modulok importálása
from .config import config
from .scheduler import scheduler

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

# 3. Adatmodell (OOP)
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

# 5. Helper függvények (Funkcionális)
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
                "units": "metric"  # Már metric-ben kérjük
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "city": data["name"],
                "temperature": data["main"]["temp"],  # Már Celsiusban
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"]
            }
        else:
            logger.error(f"API hiba ({response.status_code}): {city}")
            
    except Exception as e:
        logger.error(f"Hiba API hívásnál ({city}): {e}")
    
    return None

def save_weather_to_db(db: Session, weather_data: dict):
    """Időjárás adat mentése adatbázisba"""
    record = WeatherRecord(**weather_data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# 6. CRUD műveletek (Procedurális)
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

# 7. FastAPI alkalmazás
app = FastAPI(
    title="Weather Dashboard API",
    version="2.0",
    description="Időjárás adatok REST API"
)

# CORS beállítás
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Minden domain engedélyezve
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 8. API végpontok
@app.get("/")
def root():
    """Főoldal"""
    return {
        "service": "Weather Dashboard API",
        "version": "2.0",
        "status": "running",
        "scheduler": "active" if scheduler.is_running else "inactive",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "weather": "/api/weather?city=Budapest",
            "history": "/api/weather/history?city=Budapest",
            "stats": "/api/weather/stats?city=Budapest",
            "cities": "/api/cities",
            "refresh": "/api/refresh"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": "connected",
        "scheduler": scheduler.is_running
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
                return WeatherResponse.from_orm(record)  # Régi adatot visszaadunk
            raise HTTPException(404, f"Nem található időjárás adat: {city}")
        
        # Új rekord mentése
        record = save_weather_to_db(db, weather_data)
    
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
    hours: int = Query(24, ge=1, le=720),  # Max 30 nap
    db: Session = Depends(get_db)
):
    """Statisztikák"""
    stats = get_weather_stats(db, city, hours)
    if not stats:
        raise HTTPException(404, f"Nincs elég adat {city} városhoz az elmúlt {hours} órában")
    return stats

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
    """Konfiguráció lekérdezése (csak olvasható információk)"""
    return {
        "schedule_interval": config.SCHEDULE_INTERVAL,
        "default_cities": config.DEFAULT_CITIES,
        "scheduler_status": "active" if scheduler.is_running else "inactive"
    }

# 9. Alkalmazás indítás/leállítás
@app.on_event("startup")
def startup_event():
    """Alkalmazás indításakor"""
    logger.info("🚀 Weather API elindul...")
    
    # Konfiguráció validálása
    if config.validate():
        logger.info("✅ Konfiguráció OK")
        
        # Scheduler indítása
        scheduler.start()
        logger.info("⏰ Scheduler elindítva")
    else:
        logger.warning("⚠️  Alkalmazás indult, de konfiguráció hiányos")

@app.on_event("shutdown")
def shutdown_event():
    """Alkalmazás leállításakor"""
    logger.info("🛑 Alkalmazás leállítása...")
    scheduler.stop()
    logger.info("✅ Scheduler leállítva")

# 10. Futtatás
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)