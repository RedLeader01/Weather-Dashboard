"""FastAPI alkalmazás"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from . import crud, schemas, models
from .database import engine, get_db
from .weather_service import WeatherService
from .config import settings
from .scheduler import scheduler

# Logging beállítás
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adatbázis táblák létrehozása
models.Base.metadata.create_all(bind=engine)

# FastAPI alkalmazás
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Időjárás Dashboard API"
)

# CORS beállítás
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Szolgáltatás
weather_service = WeatherService()

@app.on_event("startup")
async def startup_event():
    """Alkalmazás indításakor"""
    logger.info("Starting Weather Dashboard API")
    scheduler.start(settings.SCHEDULE_INTERVAL_MINUTES)

@app.on_event("shutdown")
async def shutdown_event():
    """Alkalmazás leállításakor"""
    logger.info("Shutting down Weather Dashboard API")
    scheduler.stop()

@app.get("/", tags=["Root"])
async def root():
    """Gyökér végpont"""
    return {
        "message": "Weather Dashboard API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check végpont"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/weather/current", response_model=schemas.WeatherResponse, tags=["Weather"])
async def get_current_weather(
    city: str = Query(..., example="Budapest"),
    db: Session = Depends(get_db)
):
    """Aktuális időjárás lekérdezése"""
    # Először próbáljuk az adatbázisból
    weather = crud.get_latest_weather(db, city)
    
    if not weather:
        # Ha nincs adatbázisban, kérjük le az API-tól
        api_weather = weather_service.get_weather_by_city(city)
        if not api_weather:
            raise HTTPException(status_code=404, detail=f"Weather data not found for {city}")
        
        # Mentés adatbázisba
        weather_create = schemas.WeatherCreate(**api_weather)
        weather = crud.create_weather_data(db, weather_create)
    
    return weather

@app.get("/api/weather/history", response_model=List[schemas.WeatherResponse], tags=["Weather"])
async def get_weather_history(
    city: str = Query(..., example="Budapest"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Időjárás előzmények"""
    return crud.get_weather_by_city(db, city, limit)

@app.get("/api/weather/stats", response_model=schemas.WeatherStats, tags=["Weather"])
async def get_weather_stats(
    city: str = Query(..., example="Budapest"),
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """Statisztikák"""
    stats = crud.get_weather_stats(db, city, hours)
    if not stats:
        raise HTTPException(status_code=404, detail=f"No data found for {city} in the last {hours} hours")
    return stats

@app.get("/api/weather/cities", tags=["Weather"])
async def get_all_cities(db: Session = Depends(get_db)):
    """Összes város"""
    return {"cities": crud.get_all_cities(db)}

@app.get("/api/weather/multiple", response_model=schemas.MultiCityWeather, tags=["Weather"])
async def get_multiple_cities_weather(
    cities: str = Query("Budapest,Debrecen,Szeged"),
    db: Session = Depends(get_db)
):
    """Több város időjárása"""
    city_list = [city.strip() for city in cities.split(",")]
    weather_data = crud.get_multi_city_weather(db, city_list)
    
    return schemas.MultiCityWeather(cities=weather_data)

@app.post("/api/weather/refresh", tags=["Admin"])
async def refresh_weather_data():
    """Manuális adatfrissítés"""
    scheduler.fetch_and_store_weather()
    return {"message": "Weather data refresh initiated"}