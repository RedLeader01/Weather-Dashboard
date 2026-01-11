"""7 napos előrejelzés kártyák - Pure Streamlit komponensek"""
import streamlit as st
from utils import get_weekday, format_date, get_weather_icon, get_pop_emoji

def create_forecast_card(forecast: dict, is_today: bool = False):
    """Egy nap előrejelzésének megjelenítése Streamlit komponensekkel"""
    
    weekday = get_weekday(forecast['date'])
    date_formatted = format_date(forecast['date'])
    
    icon_url = get_weather_icon(forecast.get('icon', ''), force_day_icon=True)
    
    pop_icon, pop_color = get_pop_emoji(forecast.get('pop', 0))
    
    # Kártya konténer használata
    with st.container():
        # Kártya fejléc
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if is_today:
                st.markdown(f"### 🎯 **{weekday}** - {date_formatted} (Ma)")
            else:
                st.markdown(f"### **{weekday}** - {date_formatted}")
        
        with col2:
            if icon_url and icon_url != "https://openweathermap.org/img/wn/@2x.png":
                st.image(icon_url, width=60)
        
        # Fő információk
        st.markdown(f"## {forecast['day_temp']:.1f}°C")
        st.markdown(f"*{forecast['description'].capitalize()}*")
        
        # Részletes adatok - Grid szerűen
        st.markdown("---")
        
        # 4 oszlop a metrikáknak
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            st.metric("🌙 Éjszaka", f"{forecast['night_temp']:.1f}°C")
        
        with col4:
            st.metric("📈 Max", f"{forecast['max_temp']:.1f}°C")
        
        with col5:
            st.metric("📉 Min", f"{forecast['min_temp']:.1f}°C")
        
        with col6:
            st.metric("💧 Pára", f"{forecast['humidity']}%")
        
        # Csapadék, szél, nyomás
        st.markdown("---")
        
        col7, col8, col9 = st.columns(3)
        
        with col7:
            st.markdown(f"**{pop_icon} Csapadék:** {forecast.get('pop', 0):.1f}%")
        
        with col8:
            st.markdown(f"**💨 Szél:** {forecast['wind_speed']:.1f} m/s")
        
        with col9:
            st.markdown(f"**🎯 Nyomás:** {forecast['pressure']} hPa")
        
        # Elválasztó vonal
        st.markdown("---")

def create_compact_forecast_card(forecast: dict, is_today: bool = False):
    """Kompakt előrejelzés kártya (kisebb változat)"""
    
    weekday = get_weekday(forecast['date'])
    date_formatted = format_date(forecast['date'])
    
    # HASZNÁLJUK A UTILS.PY FÜGGVÉNYT!
    icon_url = get_weather_icon(forecast.get('icon', ''), force_day_icon=True)
    
    # Kártya konténer
    with st.container():
        # Fejléc
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if is_today:
                st.markdown(f"**🎯 {weekday}**")
            else:
                st.markdown(f"**{weekday}**")
            st.caption(date_formatted)
        
        with col2:
            if icon_url and icon_url != "https://openweathermap.org/img/wn/@2x.png":
                st.image(icon_url, width=40)
        
        with col3:
            st.markdown(f"**{forecast['day_temp']:.1f}°C**")
        
        # Leírás
        st.caption(forecast['description'].capitalize())