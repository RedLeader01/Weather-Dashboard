"""Segédfüggvények a frontendhez"""
from datetime import datetime, timedelta

def format_temperature(temp: float) -> str:
    """Hőmérséklet formázása"""
    return f"{temp:.1f}°C"

def format_time(timestamp_str: str) -> str:
    """Időbélyeg formázása"""
    try:
        if timestamp_str:
            # Távolítsuk el a 'Z'-t és konvertáljunk
            if 'Z' in timestamp_str:
                timestamp_str = timestamp_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%Y.%m.%d %H:%M")
    except:
        pass
    return timestamp_str

def get_weekday(date_str: str) -> str:
    """Dátum szöveggé konvertálása (hét napja)"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]
        today = datetime.now().date()
        
        if date_obj.date() == today:
            return "Ma"
        elif date_obj.date() == today + timedelta(days=1):
            return "Holnap"
        else:
            return weekdays[date_obj.weekday()]
    except:
        return date_str

def format_date(date_str: str) -> str:
    """Dátum formázása"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%m.%d")
    except:
        return date_str

def get_weather_icon(icon_code: str, force_day_icon: bool = False) -> str:
    """Időjárás ikon URL generálása"""
    if icon_code:
        # Ha nappali ikont kérünk, de az éjszakai van
        if force_day_icon and icon_code.endswith('n'):
            icon_code = icon_code[:-1] + 'd'
        return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    return ""

def get_pop_emoji(pop_value: float) -> tuple:
    """Csapadék valószínűség alapján emoji és szín"""
    try:
        pop_value = float(pop_value)
    except (ValueError, TypeError):
        pop_value = 0
    
    if pop_value > 70:
        return "🌧️", "#667eea"
    elif pop_value > 40:
        return "🌦️", "#95E1D3"
    elif pop_value > 10:
        return "⛅", "#FFD166"
    else:
        return "☀️", "#FF6B6B"