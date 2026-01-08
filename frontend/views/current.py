"""Aktuális időjárás oldal"""
import streamlit as st
from datetime import datetime

def display(api_client, cities):
    """Aktuális időjárás megjelenítése"""
    st.markdown('<h1 class="main-header">🌤️ Aktuális Időjárás</h1>', unsafe_allow_html=True)
    
    # Város választó és frissítés
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        city = st.selectbox(
            "Válassz várost:",
            cities,
            index=0,
            key="current_city_select"
        )
    
    with col2:
        if st.button("🔄 Frissítés", use_container_width=True, key="refresh_current"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    with col3:
        if st.button("🌤️ Előrejelzés", use_container_width=True, key="goto_forecast"):
            st.session_state.page = 'forecast'
            st.rerun()
    
    # Adatok lekérése
    with st.spinner("Időjárás adatok betöltése..."):
        data = api_client.get_current_weather(city)
    
    if data:
        # Fő információk
        from ..components.weather_cards import display_current_weather_card
        display_current_weather_card(city, data)
        
        # Gyors előrejelzés
        with st.expander("📅 Gyors 3 napos előrejelzés", expanded=False):
            forecast_data = api_client.get_weather_forecast(city, 3)
            if forecast_data and forecast_data.get('forecasts'):
                forecast_cols = st.columns(3)
                for idx, forecast in enumerate(forecast_data['forecasts']):
                    with forecast_cols[idx]:
                        from ..components.weather_cards import display_quick_forecast_card
                        display_quick_forecast_card(forecast)
    
    else:
        st.error("❌ Nem sikerült betölteni az időjárás adatokat")
        st.info("""
        **Lehetséges okok:**
        1. A backend nem fut
        2. Nincs internetkapcsolat
        3. A város nem található
        
        **Megoldások:**
        1. Indítsd el a backendet (python start.py)
        2. Ellenőrizd az internetkapcsolatot
        3. Nézd meg a Beállítások oldalt
        """)