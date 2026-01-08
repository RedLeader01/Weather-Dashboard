"""Statisztikák oldal"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def display(api_client, cities):
    """Statisztikák megjelenítése"""
    st.markdown('<h1 class="main-header">📊 Időjárás Statisztikák</h1>', unsafe_allow_html=True)
    
    # Beállítások
    col1, col2, col3 = st.columns(3)
    
    with col1:
        city = st.selectbox("Város:", cities, key="stats_city")
    
    with col2:
        hours = st.selectbox(
            "Időtartam:",
            [1, 6, 12, 24, 48, 72, 168],
            index=3,
            format_func=lambda x: f"{x} óra" if x < 24 else f"{x//24} nap",
            key="stats_hours"
        )
    
    with col3:
        show_chart = st.button("📈 Diagram generálás", use_container_width=True, key="generate_chart")
    
    # Adatok lekérése
    cache_key = f"stats_{city}_{hours}"
    
    if cache_key not in st.session_state:
        with st.spinner(f"{city} statisztikáinak számítása..."):
            data = api_client.get_weather_stats(city, hours)
            st.session_state[cache_key] = data
    else:
        data = st.session_state[cache_key]
    
    if data:
        from frontend.utils import format_time
        
        # Metrikák
        st.subheader(f"📈 Statisztikák - {city} (utolsó {hours} óra)")
        
        cols = st.columns(4)
        metrics = [
            ("🌡️ Átlag", f"{data['avg_temperature']:.1f}°C", "#FF6B6B"),
            ("📉 Minimum", f"{data['min_temperature']:.1f}°C", "#4ECDC4"),
            ("📈 Maximum", f"{data['max_temperature']:.1f}°C", "#45B7D1"),
            ("🔢 Mérések", str(data['record_count']), "#95E1D3")
        ]
        
        for col, (label, value, color) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size: 1.2rem; color: {color}; font-weight: bold;'>{label}</div>
                    <div style='font-size: 2.2rem; font-weight: bold; color: {color};'>{value}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # További információk
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **🌡️ Hőmérséklet tartomány:**  
            {data['min_temperature']:.1f}°C - {data['max_temperature']:.1f}°C
            
            **💧 Átlag páratartalom:**  
            {data['avg_humidity']:.1f}%
            
            **📊 Mérések száma:**  
            {data['record_count']} db
            
            **🕐 Utolsó frissítés:**  
            {format_time(data.get('last_update', '')) if data.get('last_update') else 'N/A'}
            """)
        
        with col2:
            # Diagram a hőmérséklet tartományhoz
            fig = go.Figure(data=[
                go.Bar(
                    x=['Minimum', 'Átlag', 'Maximum'],
                    y=[data['min_temperature'], data['avg_temperature'], data['max_temperature']],
                    marker_color=['#4ECDC4', '#FF6B6B', '#45B7D1'],
                    text=[f"{data['min_temperature']:.1f}°C", 
                          f"{data['avg_temperature']:.1f}°C", 
                          f"{data['max_temperature']:.1f}°C"],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title='Hőmérséklet statisztikák',
                yaxis_title='Hőmérséklet (°C)',
                height=300,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Időbeli változás diagram
        if show_chart:
            history_data = api_client.get_weather_history(city, min(48, hours*2))
            if history_data and len(history_data) > 1:
                st.subheader("📈 Időbeli változás")
                
                df = pd.DataFrame(history_data)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['temperature'],
                    mode='lines+markers',
                    name='Hőmérséklet',
                    line=dict(color='#FF6B6B', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['humidity'],
                    mode='lines',
                    name='Páratartalom',
                    yaxis='y2',
                    line=dict(color='#45B7D1', width=2, dash='dash')
                ))
                
                fig.update_layout(
                    title=f'{city} - Hőmérséklet és páratartalom trend',
                    xaxis_title='Idő',
                    yaxis_title='Hőmérséklet (°C)',
                    yaxis2=dict(
                        title='Páratartalom (%)',
                        overlaying='y',
                        side='right'
                    ),
                    height=400,
                    hovermode='x unified',
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error(f"❌ Nincs elég adat {city} városhoz az elmúlt {hours} órában")
        st.info("Várj, hogy a scheduler gyűjtsön több adatot.")