"""Időjárás előzmények oldal"""
import streamlit as st
import pandas as pd
from components.charts import create_temperature_chart
from utils import format_time

def display(api_client, cities):
    """Időjárás előzmények megjelenítése"""
    st.markdown('<h1 class="main-header">📈 Időjárás Előzmények</h1>', unsafe_allow_html=True)
    
    # Beállítások
    col1, col2, col3 = st.columns(3)
    
    with col1:
        city = st.selectbox("Város:", cities, key="history_city")
    
    with col2:
        limit = st.slider("Rekordok száma:", 5, 50, 20, key="history_limit")
    
    with col3:
        chart_type = st.selectbox(
            "Diagram típusa:",
            ["Vonal", "Oszlop", "Pont", "Terület"],
            key="chart_type"
        )
    
    # Adatok lekérése cache-el
    cache_key = f"history_{city}_{limit}"
    
    if cache_key not in st.session_state:
        with st.spinner(f"{city} előzményeinek betöltése..."):
            data = api_client.get_weather_history(city, limit)
            st.session_state[cache_key] = data
    else:
        data = st.session_state[cache_key]
    
    if data and len(data) > 0:

        
        # Diagram
        fig = create_temperature_chart(data, chart_type)
        if fig:
            fig.update_layout(title=f'{city} - Időjárás előzmények')
            st.plotly_chart(fig, use_container_width=True)
        
        # Statisztikák
        st.subheader("📊 Statisztikai összefoglaló")
        
        df = pd.DataFrame(data)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Átlag hőmérséklet", f"{df['temperature'].mean():.1f}°C")
        
        with col2:
            st.metric("Minimum", f"{df['temperature'].min():.1f}°C")
        
        with col3:
            st.metric("Maximum", f"{df['temperature'].max():.1f}°C")
        
        with col4:
            st.metric("Változatosság", f"{df['temperature'].std():.1f}°C")
        
        # Részletes adatok
        with st.expander("📋 Részletes adatok", expanded=False):
            display_df = df[['timestamp', 'temperature', 'humidity', 'pressure', 'wind_speed', 'description']].copy()
            display_df['timestamp'] = display_df['timestamp'].apply(format_time)
            display_df.columns = ['Idő', 'Hőmérséklet (°C)', 'Páratartalom (%)', 'Nyomás (hPa)', 
                                 'Szél (m/s)', 'Leírás']
            st.dataframe(display_df, use_container_width=True, height=400)
    
    else:
        st.warning(f"⚠️ Nincs elég adat {city} városhoz")
        st.info("Használd a '🔄 Frissítés' gombot az oldalsávban több adat gyűjtéséhez.")