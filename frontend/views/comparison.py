"""Városok összehasonlítása oldal"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def display(api_client, cities):
    """Városok összehasonlítása"""
    st.markdown('<h1 class="main-header">🏙️ Városok Összehasonlítása</h1>', unsafe_allow_html=True)
    
    # Városok kiválasztása
    st.subheader("📍 Városok kiválasztása")
    
    selected_cities = st.multiselect(
        "Válassz városokat összehasonlításhoz:",
        cities,
        default=st.session_state.selected_cities,
        key="comparison_cities",
        max_selections=6
    )
    
    # Frissítsük a session state-et
    st.session_state.selected_cities = selected_cities
    
    # Információ
    st.caption(f"Kiválasztva: {len(selected_cities)} város")
    
    if len(selected_cities) < 2:
        st.warning("⚠️ Válassz legalább 2 várost az összehasonlításhoz!")
        
        # Automatikus javaslat
        if len(cities) >= 2:
            st.info(f"**Javaslat:** {cities[0]} és {cities[1]}")
            if st.button("🔄 Automatikus kiválasztás", key="auto_select"):
                st.session_state.selected_cities = cities[:2]
                st.rerun()
        return
    
    # Adatok gyűjtése
    with st.spinner("Városok adatainak betöltése..."):
        cities_data = []
        failed_cities = []
        
        progress_bar = st.progress(0)
        for i, city in enumerate(selected_cities):
            data = api_client.get_current_weather(city)
            if data:
                cities_data.append(data)
            else:
                failed_cities.append(city)
                # Próbáljuk meg az előzményekből az utolsó adatot
                history = api_client.get_weather_history(city, 1)
                if history and len(history) > 0:
                    cities_data.append(history[0])
                else:
                    st.warning(f"Nincs adat a(z) {city} városhoz")
            
            progress_bar.progress((i + 1) / len(selected_cities))
        
        if failed_cities:
            st.warning(f"⚠️ Néhány város adatai nem elérhetők: {', '.join(failed_cities)}")
    
    if len(cities_data) < 2:
        st.error("❌ Nincs elég adat az összehasonlításhoz!")
        return
    
    # Diagramok
    st.subheader("📊 Hőmérséklet összehasonlítás")
    
    # 1. Oszlop diagram
    fig1 = go.Figure(data=[
        go.Bar(
            x=[d['city'] for d in cities_data],
            y=[d['temperature'] for d in cities_data],
            text=[f"{d['temperature']:.1f}°C" for d in cities_data],
            textposition='auto',
            marker_color='#95E1D3',
            hovertemplate='<b>%{x}</b><br>Hőmérséklet: %{y:.1f}°C<br>Páratartalom: %{customdata}%<extra></extra>',
            customdata=[d['humidity'] for d in cities_data]
        )
    ])
    
    fig1.update_layout(
        title='Városok hőmérséklet összehasonlítása',
        yaxis_title='Hőmérséklet (°C)',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 2. Táblázatos összehasonlítás
    st.subheader("📋 Összehasonlító táblázat")
    
    from ..utils import format_time
    
    comparison_data = []
    for data in cities_data:
        comparison_data.append({
            '🏙️ Város': data['city'],
            '🌡️ Hőmérséklet': f"{data['temperature']:.1f}°C",
            '💧 Páratartalom': f"{data['humidity']}%",
            '🎯 Nyomás': f"{data.get('pressure', 'N/A')} hPa",
            '💨 Szél': f"{data.get('wind_speed', 'N/A')} m/s",
            '☁️ Leírás': data['description'].capitalize(),
            '🕐 Frissítve': format_time(data['timestamp'])
        })
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "🏙️ Város": st.column_config.TextColumn("Város", width="medium"),
            "🌡️ Hőmérséklet": st.column_config.TextColumn("Hőmérséklet", width="small"),
            "💧 Páratartalom": st.column_config.TextColumn("Pára", width="small"),
            "🎯 Nyomás": st.column_config.TextColumn("Nyomás", width="small"),
            "💨 Szél": st.column_config.TextColumn("Szél", width="small"),
            "☁️ Leírás": st.column_config.TextColumn("Időjárás", width="medium"),
            "🕐 Frissítve": st.column_config.TextColumn("Frissítve", width="medium"),
        }
    )
    
    # Exportálás lehetősége
    if st.button("💾 Adatok exportálása CSV-ként", key="export_csv"):
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV letöltése",
            data=csv,
            file_name=f"varosok_osszehasonlitasa_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )