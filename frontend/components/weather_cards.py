"""Időjárás kártyák komponensek"""
import streamlit as st

def get_forecast_card_html(forecast: dict, is_today: bool = False) -> str:
    """Egy nap előrejelzésének HTML generálása"""
    # ABSZOLÚT IMPORT a saját utils-ból
    from frontend.utils import get_weekday, format_date, get_weather_icon, get_pop_emoji
    
    weekday = get_weekday(forecast['date'])
    date_formatted = format_date(forecast['date'])
    icon_url = get_weather_icon(forecast['icon'])
    pop_icon, pop_color = get_pop_emoji(forecast.get('pop', 0))
    
    # Kártya stílus
    card_class = "weather-card" if is_today else "forecast-card"
    highlight_class = "today-highlight" if is_today else ""
    
    # Színek
    text_color = "white" if is_today else "#333333"
    border_color = "rgba(255,255,255,0.3)" if is_today else "rgba(0,0,0,0.1)"
    opacity = "0.9" if is_today else "0.8"
    
    # HTML generálása
    html = f"""
    <div class="{card_class} {highlight_class}" style="color: {text_color} !important;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
            <div>
                <div style="font-size: 1.2rem; font-weight: bold; margin: 0; color: {text_color} !important;">{weekday}</div>
                <div style="font-size: 0.9rem; opacity: {opacity}; margin: 0; color: {text_color} !important;">{date_formatted}</div>
            </div>
            <div style="background: rgba(255,255,255,0.2); border-radius: 50%; padding: 5px;">
                <img src="{icon_url}" style="width: 50px; height: 50px;">
            </div>
        </div>
        
        <div style="text-align: center; margin: 15px 0;">
            <div style="font-size: 2.5rem; font-weight: bold; margin: 0; color: {text_color} !important;">{forecast['day_temp']}°C</div>
            <div style="font-size: 1rem; margin: 5px 0; color: {text_color} !important;">{forecast['description'].capitalize()}</div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0;">
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; opacity: {opacity}; color: {text_color} !important;">🌙 Éjszaka</div>
                <div style="font-size: 1.1rem; font-weight: bold; color: {text_color} !important;">{forecast['night_temp']}°C</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; opacity: {opacity}; color: {text_color} !important;">📈 Max</div>
                <div style="font-size: 1.1rem; font-weight: bold; color: {text_color} !important;">{forecast['max_temp']}°C</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; opacity: {opacity}; color: {text_color} !important;">📉 Min</div>
                <div style="font-size: 1.1rem; font-weight: bold; color: {text_color} !important;">{forecast['min_temp']}°C</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; opacity: {opacity}; color: {text_color} !important;">💧 Pára</div>
                <div style="font-size: 1.1rem; font-weight: bold; color: {text_color} !important;">{forecast['humidity']}%</div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 15px; padding-top: 10px; border-top: 1px dashed {border_color};">
            <div style="color: {pop_color}; font-weight: bold; font-size: 0.9rem;">
                {pop_icon} Csapadék: {forecast.get('pop', 0)}%
            </div>
        </div>
    </div>
    """
    return html

def display_current_weather_card(city: str, weather_data: dict):
    """Aktuális időjárás kártya"""
    from frontend.utils import format_time, get_weather_icon
    
    icon_url = get_weather_icon(weather_data.get('icon'))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class='weather-card'>
            <h1 style='font-size: 4.5rem; margin: 0; color: white !important;'>{weather_data['temperature']:.1f}°C</h1>
            <h2 style='margin-top: 0; color: white !important;'>{city}</h2>
            <p style='font-size: 1.8rem; margin-bottom: 5px; color: white !important;'>{weather_data['description'].capitalize()}</p>
            <p style='opacity: 0.9; color: white !important;'>Utolsó frissítés: {format_time(weather_data['timestamp'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if icon_url:
            st.image(icon_url, width=180)
        else:
            st.info("⛅ Ikon nem elérhető")
    
    # Metrikák
    st.subheader("📊 Időjárás részletek")
    
    cols = st.columns(4)
    metrics = [
        ("💧 Páratartalom", f"{weather_data['humidity']}%", "#4ECDC4"),
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
    """Gyors előrejelzés kártya (3 napos)"""
    from frontend.utils import get_weekday, get_weather_icon
    
    weekday = get_weekday(forecast['date'])
    icon_url = get_weather_icon(forecast['icon'])
    
    st.markdown(f"""
    <div class='quick-forecast-card'>
        <div style='font-weight: bold; color: #333333 !important;'>{weekday}</div>
        <div class='weather-icon-container'>
            <img src='{icon_url}' style='width: 50px; height: 50px;'>
        </div>
        <div style='font-size: 1.2rem; font-weight: bold; color: #333333 !important; margin-top: 5px;'>{forecast['day_temp']}°C</div>
        <div style='font-size: 0.9rem; color: #333333 !important;'>{forecast['description']}</div>
    </div>
    """, unsafe_allow_html=True)