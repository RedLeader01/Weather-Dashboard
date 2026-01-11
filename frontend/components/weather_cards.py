"""Időjárás kártyák komponensek"""
import streamlit as st
from utils import get_weekday, format_date, get_weather_icon, get_pop_emoji, format_time

def display_current_weather_card(city: str, weather_data: dict):
    """Aktuális időjárás kártya"""
    if not weather_data:
        st.error("Nincs időjárás adat!")
        return
        
    icon_url = get_weather_icon(weather_data.get('icon'))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        current_temp = weather_data.get('temperature', 'N/A')
        if isinstance(current_temp, (int, float)):
            temp_display = f"{current_temp:.1f}°C"
        else:
            temp_display = f"{current_temp}°C"
            
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 25px; color: white !important; margin: 10px 0; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
            <h1 style="font-size: 4.5rem; margin: 0; color: white !important;">{temp_display}</h1>
            <h2 style="margin-top: 0; color: white !important;">{city}</h2>
            <p style="font-size: 1.8rem; margin-bottom: 5px; color: white !important;">{weather_data.get('description', 'N/A').capitalize()}</p>
            <p style="opacity: 0.9; color: white !important;">Utolsó frissítés: {format_time(weather_data.get('timestamp', ''))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if icon_url and icon_url != "https://openweathermap.org/img/wn/@2x.png":
            st.image(icon_url, width=180)
        else:
            st.info("⛅ Ikon nem elérhető")
    
    # Metrikák
    st.subheader("📊 Időjárás részletek")
    
    cols = st.columns(4)
    metrics = [
        ("💧 Páratartalom", f"{weather_data.get('humidity', 'N/A')}%", "#4ECDC4"),
        ("🎯 Légnyomás", f"{weather_data.get('pressure', 'N/A')} hPa", "#FF6B6B"),
        ("💨 Szélsebesség", f"{weather_data.get('wind_speed', 'N/A')} m/s", "#95E1D3"),
        ("📍 Ország", weather_data.get('country', 'HU'), "#FFD166")
    ]
    
    for col, (label, value, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div style='background: {color}20; border-radius: 12px; padding: 20px; text-align: center; color: #333333 !important;'>
                <div style='font-size: 1.2rem; color: {color}; font-weight: bold;'>{label}</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: #333333 !important;'>{value}</div>
            </div>
            """, unsafe_allow_html=True)

def display_quick_forecast_card(forecast: dict):
    """Gyors előrejelzés kártya (3 napos) - Egyszerű Streamlit komponensek"""
    
    weekday = get_weekday(forecast['date'])
    
    icon_url = get_weather_icon(forecast.get('icon', ''), force_day_icon=True)
    
    # Streamlit konténer használata
    with st.container():
        # Kártya fejléc
        st.markdown(f"**{weekday}**")
        
        # Ikon és hőmérséklet
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if icon_url and icon_url != "https://openweathermap.org/img/wn/@2x.png":
                st.image(icon_url, width=60)
        
        with col2:
            st.markdown(f"### {forecast['day_temp']:.1f}°C")
        
        # Leírás
        st.caption(forecast['description'].capitalize())
        
        # Elválasztó vonal
        st.markdown("---")