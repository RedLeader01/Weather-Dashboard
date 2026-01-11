"""Beállítások oldal"""
import streamlit as st
import requests
import time

def display(api_client, cities):
    """Beállítások oldal"""
    st.markdown('<h1 class="main-header">⚙️ Beállítások</h1>', unsafe_allow_html=True)
    
    # API konfiguráció
    st.subheader("🔌 API Konfiguráció")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_api_url = st.text_input(
            "Backend URL:",
            value=st.session_state.get('api_url', api_client.base_url),
            help="A saját FastAPI backend címe (pl: http://localhost:8000)",
            key="api_url_input"
        )
        
        if st.button("💾 Mentés", key="save_api_url"):
            if new_api_url != api_client.base_url:
                api_client.base_url = new_api_url
                st.session_state.api_url = new_api_url
                st.success("✅ Backend URL frissítve!")
                time.sleep(1)
                st.rerun()
    
    with col2:
        st.write("Backend állapot:")
        try:
            response = requests.get(f"{api_client.base_url}/health", timeout=3)
            if response.status_code == 200:
                st.success("✅ Backend elérhető")
                health_data = response.json()
                st.caption(f"Status: {health_data.get('status', 'N/A')}")
            else:
                st.error(f"❌ Backend hiba: {response.status_code}")
        except:
            st.error("❌ Backend nem elérhető")
    
    st.divider()
    
    # Adatbázis információk
    st.subheader("🗄️ Adatbázis információk")
    
    cities_list = api_client.get_all_cities()
    if cities_list:
        st.write(f"**Városok az adatbázisban:** {len(cities_list)}")
        
        if cities_list:
            cities_html = " ".join([f'<span class="city-chip">{city}</span>' for city in sorted(cities_list)])
            st.markdown(cities_html, unsafe_allow_html=True)
    else:
        st.warning("Nem lehet kapcsolódni az adatbázishoz")
    
    # Rendszer információk
    st.subheader("ℹ️ Rendszer információk")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Frontend", "Streamlit")
        st.metric("Backend", "FastAPI")
    
    with col2:
        st.metric("Adatbázis", "SQLite")
        st.metric("Python", "3.10+")
    
    # Konfiguráció lekérése
    config_data = api_client.fetch_data("/api/config")
    if config_data:
        st.subheader("⚙️ Alkalmazás konfiguráció")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Frissítési idő", f"{config_data.get('schedule_interval', 30)} perc")
            st.metric("Alapértelmezett városok", f"{len(config_data.get('default_cities', []))}")
        
        with col2:
            scheduler_status = config_data.get('scheduler_status', 'inactive')
            st.metric("Scheduler állapot", scheduler_status)
            
            openweather_status = config_data.get('openweather_configured', False)
            openweather_text = "Konfigurálva" if openweather_status else "Nincs konfigurálva"
            st.metric("OpenWeather API", openweather_text)
    
    # Visszaállítás
    st.subheader("🔄 Visszaállítás")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Alapértelmezett városok", type="secondary", use_container_width=True):
            st.session_state.selected_cities = cities[:3]
            st.success("✅ Városok visszaállítva!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("Alapértelmezett URL", type="secondary", use_container_width=True):
            st.session_state.api_url = "http://localhost:8000"
            api_client.base_url = "http://localhost:8000"
            st.success("✅ URL visszaállítva!")
            time.sleep(1)
            st.rerun()