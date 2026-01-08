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
            # Cache törlése
            cache_keys = [k for k in st.session_state.keys() 
                         if k.startswith(f"current_{city}") or k.startswith(f"quick_forecast_{city}")]
            for key in cache_keys:
                st.session_state.pop(key, None)
            st.rerun()
    
    with col3:
        if st.button("🌤️ Előrejelzés", use_container_width=True, key="goto_forecast"):
            st.session_state.page = 'forecast'
            st.rerun()
    
    # Adatok lekérése cache-el
    cache_key = f"current_{city}"
    
    if cache_key not in st.session_state:
        with st.spinner(f"{city} időjárás adatainak betöltése..."):
            data = api_client.get_current_weather(city)
            if data:
                st.session_state[cache_key] = data
            else:
                st.error(f"❌ Nem sikerült betölteni {city} adatait")
                return
    else:
        data = st.session_state[cache_key]
    
    if data:
        # Fő információk
        from components.weather_cards import display_current_weather_card
        display_current_weather_card(city, data)
        
        # Gyors előrejelzés
        with st.expander("📅 Gyors 3 napos előrejelzés", expanded=False):
            forecast_cache_key = f"quick_forecast_{city}"
            
            if forecast_cache_key not in st.session_state:
                forecast_data = api_client.get_weather_forecast(city, 3)
                st.session_state[forecast_cache_key] = forecast_data
            else:
                forecast_data = st.session_state[forecast_cache_key]
            
            if forecast_data and forecast_data.get('forecasts'):
                forecast_cols = st.columns(3)
                for idx, forecast in enumerate(forecast_data['forecasts']):
                    with forecast_cols[idx]:
                        from components.weather_cards import display_quick_forecast_card
                        display_quick_forecast_card(forecast)
            else:
                st.info("⚠️ Előrejelzés nem elérhető")
    
    else:
        st.error("❌ Nem sikerült betölteni az időjárás adatokat")
        
        # Diagnosztika
        with st.expander("🔧 Hibaelhárítás", expanded=False):
            st.info(f"""
            **Backend URL:** {api_client.base_url}
            **Város:** {city}
            **Idő:** {datetime.now().strftime("%H:%M:%S")}
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧪 Teszt kapcsolat", key="test_conn"):
                    health = api_client.get_health()
                    if health:
                        st.success("✅ Backend elérhető")
                    else:
                        st.error("❌ Backend nem elérhető")
            
            with col2:
                if st.button("🔄 Töröl cache", key="clear_cache_current"):
                    keys = [k for k in st.session_state.keys() 
                           if k.startswith('current_') or k.startswith('quick_forecast_')]
                    for key in keys:
                        st.session_state.pop(key, None)
                    st.success("✅ Cache törölve")
                    st.rerun()