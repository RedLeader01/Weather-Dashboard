# 🌤️ Weather Dashboard v2.2

Egy teljes értékű időjárás dashboard mikroszerviz architektúrával, 7 napos előrejelzéssel.

## 📋 Újdonságok v2.2

### 🌤️ 7 Napos Időjárás Előrejelzés
- **Napi előrejelzés kártyák**: Minden nap külön kártyán
- **Interaktív diagramok**: Hőmérséklet, páratartalom, csapadék
- **Részletes táblázat**: Minden adat egy helyen
- **Exportálás**: CSV formátumban letölthető

## 🏗️ Architektúra
- **Backend**: FastAPI REST API (Python)
- **Frontend**: Streamlit webes felület
- **Adatbázis**: SQLite/PostgreSQL
- **Ütemező**: Automatikus adatfrissítés

## 🚀 Telepítés és Futtatás

## ▶️ Új Indítás (Moduláris verzió)

### 1. Klónozás és beállítás
```bash
git clone [repository-url]
cd weather-dashboard

# Virtual environment
python -m venv weather-dashboard

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Függőségek
pip install -r requirements.txt

# Konfiguráció
cp .env.example .env
# Szerkeszd a .env fájlt és add hozzá az OpenWeather API kulcsodat
