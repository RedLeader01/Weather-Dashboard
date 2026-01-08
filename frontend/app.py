"""
🌤️ Weather Dashboard Frontend - Javított verzió
Streamlit felület az időjárás adatok megjelenítéséhez
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json

# ============================================
# 1. KONFIGURÁCIÓ ÉS BEÁLLÍTÁSOK
# ============================================

# Oldal konfiguráció
st.set_page_config(
    page_title="Időjárás Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stílusok
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 25px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    .city-chip {
        display: inline-block;
        background: #e3f2fd;
        color: #1E88E5;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 3px;
        font-weight: 500;
    }
    .api-key-display {
        font-family: 'Courier New', monospace;
        background: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 2. OSZTÁLYOK ÉS HELPER FÜGGVÉNYEK
# ============================================

class WeatherApp:
    """Időjárás alkalmazás fő osztálya"""
    
    def __init__(self):
        """Inicializálás"""
        self.init_session_state()
        self.cities = [
            "Budapest", "Debrecen", "Szeged", 
            "Pécs", "Győr", "Miskolc", "Nyíregyháza"
        ]
        self.api_url = st.session_state.get('api_url', 'http://localhost:8000')
        self.api_key = st.session_state.get('api_key', '')
        
    def init_session_state(self):
        """Session state inicializálása"""
        if 'page' not in st.session_state:
            st.session_state.page = 'current'
        if 'api_url' not in st.session_state:
            st.session_state.api_url = 'http://localhost:8000'
        if 'api_key' not in st.session_state:
            st.session_state.api_key = ''
        if 'show_api_key' not in st.session_state:
            st.session_state.show_api_key = False
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
        if 'selected_cities' not in st.session_state:
            st.session_state.selected_cities = ["Budapest", "Debrecen", "Szeged"]
    
    def fetch_data(self, endpoint, params=None):
        """
        API hívás a backendhez
        
        Args:
            endpoint: API végpont (pl. '/api/weather')
            params: Query paraméterek
            
        Returns:
            dict vagy list: API válasz
        """
        try:
            url = f"{self.api_url}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                st.warning(f"Nincs adat ehhez a lekérdezéshez: {params}")
                return None
            else:
                st.error(f"API hiba ({response.status_code}): {response.text[:100]}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Nem lehet csatlakozni az API-hoz: {self.api_url}")
            return None
        except requests.exceptions.Timeout:
            st.warning("⏰ API hívás időtúllépés, próbáld újra")
            return None
        except Exception as e:
            st.error(f"Hiba történt: {str(e)}")
            return None
    
    def get_weather_icon(self, icon_code):
        """Időjárás ikon URL generálása"""
        if icon_code:
            return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        return None
    
    def format_temperature(self, temp):
        """Hőmérséklet formázása"""
        return f"{temp:.1f}°C"
    
    def format_time(self, timestamp_str):
        """Időbélyeg formázása"""
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%Y.%m.%d %H:%M")
        except:
            return timestamp_str

# ============================================
# 3. OLDALSÁV (SIDEBAR) - TISZTÍTVA
# ============================================

def display_sidebar(app):
    """Oldalsáv megjelenítése - API beállítások nélkül"""
    with st.sidebar:
        # Logo és cím
        st.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <h1 style="color: #1E88E5; margin-bottom: 0;">🌤️</h1>
            <h2 style="color: #1E88E5; margin-top: 0;">Időjárás Dashboard</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigáció - GOMBOKKAL
        st.subheader("📍 Navigáció")
        
        # Gombok soronként
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🏠 Aktuális", use_container_width=True, 
                        type="primary" if st.session_state.page == 'current' else "secondary"):
                st.session_state.page = 'current'
                st.rerun()
        
        with col2:
            if st.button("📈 Előzmények", use_container_width=True,
                        type="primary" if st.session_state.page == 'history' else "secondary"):
                st.session_state.page = 'history'
                st.rerun()
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("📊 Statisztikák", use_container_width=True,
                        type="primary" if st.session_state.page == 'stats' else "secondary"):
                st.session_state.page = 'stats'
                st.rerun()
        
        with col4:
            if st.button("🏙️ Összehasonlítás", use_container_width=True,
                        type="primary" if st.session_state.page == 'comparison' else "secondary"):
                st.session_state.page = 'comparison'
                st.rerun()
        
        # Beállítások gomb külön sorban
        if st.button("⚙️ Beállítások", use_container_width=True,
                    type="primary" if st.session_state.page == 'settings' else "secondary"):
            st.session_state.page = 'settings'
            st.rerun()
        
        st.divider()
        
        # Gyors műveletek
        st.subheader("⚡ Gyors műveletek")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Frissítés", use_container_width=True, help="Adatok frissítése"):
                response = app.fetch_data("/api/refresh")
                if response:
                    st.success("✅ Adatok frissítve!")
                    st.session_state.last_refresh = datetime.now()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Frissítés sikertelen")
        
        with col2:
            if st.button("🗑️ Cache", use_container_width=True, help="Cache törlése"):
                st.cache_data.clear()
                st.success("✅ Cache törölve")
                time.sleep(1)
                st.rerun()
        
        st.divider()
        
        # Információk
        st.caption(f"**Backend:** {app.api_url}")
        st.caption(f"**Frissítve:** {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        # API státusz
        if st.button("📊 Állapot", use_container_width=True, type="secondary"):
            data = app.fetch_data("/api/cities")
            if data:
                st.info(f"**{len(data.get('cities', []))} város**")
            else:
                st.error("❌ Backend nem elérhető")

# ============================================
# 4. OLDALAK MEGJELENÍTÉSE
# ============================================

def display_current_weather(app):
    """Aktuális időjárás megjelenítése"""
    st.markdown('<h1 class="main-header">🌤️ Aktuális Időjárás</h1>', unsafe_allow_html=True)
    
    # Város választó és frissítés
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        city = st.selectbox(
            "Válassz várost:",
            app.cities,
            index=0,
            key="current_city_select"
        )
    
    with col2:
        if st.button("🔄 Frissítés", use_container_width=True, key="refresh_current"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    with col3:
        if st.button("📊 Statisztikák", use_container_width=True, key="goto_stats"):
            st.session_state.page = 'stats'
            st.rerun()
    
    # Adatok lekérése
    with st.spinner("Időjárás adatok betöltése..."):
        data = app.fetch_data("/api/weather", {"city": city})
    
    if data:
        # Fő információk
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div class='weather-card'>
                <h1 style='font-size: 4.5rem; margin: 0;'>{app.format_temperature(data['temperature'])}</h1>
                <h2 style='margin-top: 0;'>{city}</h2>
                <p style='font-size: 1.8rem; margin-bottom: 5px;'>{data['description'].capitalize()}</p>
                <p style='opacity: 0.9;'>Utolsó frissítés: {app.format_time(data['timestamp'])}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Ikon megjelenítése
            if data.get('icon'):
                icon_url = app.get_weather_icon(data['icon'])
                st.image(icon_url, width=180)
            else:
                st.info("⛅ Ikon nem elérhető")
        
        # Metrikák
        st.subheader("📊 Időjárás részletek")
        
        cols = st.columns(4)
        metrics = [
            ("💧 Páratartalom", f"{data['humidity']}%", "#4ECDC4"),
            ("🎯 Légnyomás", f"{data.get('pressure', 'N/A')} hPa", "#FF6B6B"),
            ("💨 Szélsebesség", f"{data.get('wind_speed', 'N/A')} m/s", "#95E1D3"),
            ("📍 Ország", data.get('country', 'HU'), "#FFD166")
        ]
        
        for col, (label, value, color) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                <div style='background: {color}20; border-radius: 12px; padding: 20px; text-align: center;'>
                    <div style='font-size: 1.2rem; color: {color}; font-weight: bold;'>{label}</div>
                    <div style='font-size: 1.8rem; font-weight: bold;'>{value}</div>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.error("❌ Nem sikerült betölteni az időjárás adatokat")
        st.info("""
        **Lehetséges okok:**
        1. A backend nem fut
        2. Nincs internetkapcsolat
        3. A város nem található
        """)

def display_history(app):
    """Időjárás előzmények megjelenítése"""
    st.markdown('<h1 class="main-header">📈 Időjárás Előzmények</h1>', unsafe_allow_html=True)
    
    # Beállítások
    col1, col2, col3 = st.columns(3)
    
    with col1:
        city = st.selectbox("Város:", app.cities, key="history_city")
    
    with col2:
        limit = st.slider("Rekordok száma:", 5, 50, 20, key="history_limit")
    
    with col3:
        chart_type = st.selectbox(
            "Diagram típusa:",
            ["Vonal", "Oszlop", "Pont"],
            key="chart_type"
        )
    
    # Adatok lekérése
    with st.spinner("Előzmények betöltése..."):
        data = app.fetch_data("/api/weather/history", {"city": city, "limit": limit})
    
    if data and len(data) > 0:
        # DataFrame készítése
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        df['time_formatted'] = df['timestamp'].dt.strftime('%m.%d %H:%M')
        
        # Diagram
        fig = go.Figure()
        
        if chart_type == "Vonal":
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                mode='lines+markers',
                name='Hőmérséklet',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8, color='#FF6B6B'),
                hovertemplate='<b>%{x|%H:%M}</b><br>Hőmérséklet: %{y:.1f}°C<extra></extra>'
            ))
        elif chart_type == "Oszlop":
            fig.add_trace(go.Bar(
                x=df['time_formatted'],
                y=df['temperature'],
                name='Hőmérséklet',
                marker_color='#4ECDC4',
                hovertemplate='<b>%{x}</b><br>Hőmérséklet: %{y:.1f}°C<extra></extra>'
            ))
        else:  # Pont
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                mode='markers',
                name='Hőmérséklet',
                marker=dict(size=10, color=df['humidity'], colorscale='Viridis', showscale=True),
                hovertemplate='<b>%{x|%H:%M}</b><br>Hőmérséklet: %{y:.1f}°C<br>Páratartalom: %{marker.color}%<extra></extra>'
            ))
        
        # Második tengely a páratartalomhoz
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['humidity'],
            mode='lines',
            name='Páratartalom',
            yaxis='y2',
            line=dict(color='#45B7D1', width=2, dash='dash'),
            hovertemplate='<b>%{x|%H:%M}</b><br>Páratartalom: %{y}%<extra></extra>'
        ))
        
        # Layout
        fig.update_layout(
            title=f'{city} - Időjárás előzmények',
            xaxis_title='Idő',
            yaxis_title='Hőmérséklet (°C)',
            yaxis=dict(titlefont=dict(color='#FF6B6B'), tickfont=dict(color='#FF6B6B')),
            yaxis2=dict(
                title='Páratartalom (%)',
                titlefont=dict(color='#45B7D1'),
                tickfont=dict(color='#45B7D1'),
                overlaying='y',
                side='right'
            ),
            height=500,
            template='plotly_white',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Részletes adatok
        with st.expander("📋 Részletes adatok", expanded=False):
            display_df = df[['timestamp', 'temperature', 'humidity', 'pressure', 'wind_speed', 'description']].copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y.%m.%d %H:%M')
            display_df.columns = ['Idő', 'Hőmérséklet (°C)', 'Páratartalom (%)', 'Nyomás (hPa)', 
                                 'Szél (m/s)', 'Leírás']
            st.dataframe(display_df, use_container_width=True)
    
    else:
        st.warning(f"⚠️ Nincs elég adat {city} városhoz")
        st.info("""
        **Adatok generálása:**
        1. Várj 5 percet, hogy a scheduler gyűjtsön adatot
        2. Használd a '🔄 Frissítés' gombot az oldalsávban
        3. Nyisd meg a '📊 Statisztikák' oldalt
        """)

def display_statistics(app):
    """Statisztikák megjelenítése"""
    st.markdown('<h1 class="main-header">📊 Időjárás Statisztikák</h1>', unsafe_allow_html=True)
    
    # Beállítások
    col1, col2, col3 = st.columns(3)
    
    with col1:
        city = st.selectbox("Város:", app.cities, key="stats_city")
    
    with col2:
        hours = st.selectbox(
            "Időtartam:",
            [6, 12, 24, 48, 72, 168],
            index=2,
            format_func=lambda x: f"{x} óra",
            key="stats_hours"
        )
    
    with col3:
        if st.button("📈 Diagram generálás", use_container_width=True, key="generate_chart"):
            st.session_state.show_chart = True
    
    # Adatok lekérése
    with st.spinner("Statisztikák számítása..."):
        data = app.fetch_data("/api/weather/stats", {"city": city, "hours": hours})
    
    if data:
        # Metrikák
        st.subheader(f"📈 Statisztikák - {city} (utolsó {hours} óra)")
        
        cols = st.columns(4)
        metrics = [
            ("🌡️ Átlag hőmérséklet", app.format_temperature(data['avg_temperature']), "#FF6B6B"),
            ("📉 Minimum", app.format_temperature(data['min_temperature']), "#4ECDC4"),
            ("📈 Maximum", app.format_temperature(data['max_temperature']), "#45B7D1"),
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
            {app.format_temperature(data['min_temperature'])} - {app.format_temperature(data['max_temperature'])}
            
            **💧 Átlag páratartalom:**  
            {data['avg_humidity']:.1f}%
            
            **🕐 Utolsó frissítés:**  
            {app.format_time(data.get('last_update', ''))}
            """)
        
        with col2:
            # Egyszerű diagram a hőmérséklet tartományhoz
            fig = go.Figure(data=[
                go.Bar(
                    x=['Minimum', 'Átlag', 'Maximum'],
                    y=[data['min_temperature'], data['avg_temperature'], data['max_temperature']],
                    marker_color=['#4ECDC4', '#FF6B6B', '#45B7D1'],
                    text=[app.format_temperature(data['min_temperature']), 
                          app.format_temperature(data['avg_temperature']), 
                          app.format_temperature(data['max_temperature'])],
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
        
        # Ha elérhető, jelenítsük meg az előzmények diagramját is
        if st.session_state.get('show_chart', False):
            history_data = app.fetch_data("/api/weather/history", {"city": city, "limit": 24})
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
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error(f"❌ Nincs elég adat {city} városhoz az elmúlt {hours} órában")
        st.info("""
        **Megoldások:**
        1. Várj, hogy a scheduler gyűjtsön több adatot
        2. Használd a '🔄 Frissítés' gombot
        3. Ellenőrizd, hogy a backend fut-e
        """)

def display_comparison(app):
    """Városok összehasonlítása"""
    st.markdown('<h1 class="main-header">🏙️ Városok Összehasonlítása</h1>', unsafe_allow_html=True)
    
    # Városok kiválasztása
    st.subheader("📍 Városok kiválasztása")
    
    selected_cities = st.multiselect(
        "Válassz városokat összehasonlításhoz:",
        app.cities,
        default=st.session_state.selected_cities,
        key="comparison_cities"
    )
    
    # Frissítsük a session state-et
    st.session_state.selected_cities = selected_cities
    
    # Információ
    st.caption(f"Kiválasztva: {len(selected_cities)} város")
    
    if len(selected_cities) < 2:
        st.warning("⚠️ Válassz legalább 2 várost az összehasonlításhoz!")
        
        # Automatikus javaslat
        if len(app.cities) >= 2:
            st.info(f"**Javaslat:** {app.cities[0]} és {app.cities[1]}")
            if st.button("🔄 Automatikus kiválasztás"):
                st.session_state.selected_cities = app.cities[:2]
                st.rerun()
        return
    
    # Adatok gyűjtése
    with st.spinner("Városok adatainak betöltése..."):
        cities_data = []
        failed_cities = []
        
        for city in selected_cities:
            data = app.fetch_data("/api/weather", {"city": city})
            if data:
                cities_data.append(data)
            else:
                failed_cities.append(city)
                # Próbáljuk meg az előzményekből az utolsó adatot
                history = app.fetch_data("/api/weather/history", {"city": city, "limit": 1})
                if history and len(history) > 0:
                    cities_data.append(history[0])
                else:
                    st.warning(f"Nincs adat a(z) {city} városhoz")
    
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
            text=[app.format_temperature(d['temperature']) for d in cities_data],
            textposition='auto',
            marker_color='#95E1D3',
            hovertemplate='<b>%{x}</b><br>Hőmérséklet: %{y:.1f}°C<br>Páratartalom: %{customdata}%<extra></extra>',
            customdata=[d['humidity'] for d in cities_data]
        )
    ])
    
    fig1.update_layout(
        title='Városok hőmérséklet összehasonlítása',
        yaxis_title='Hőmérséklet (°C)',
        height=400
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 2. Táblázatos összehasonlítás
    st.subheader("📋 Összehasonlító táblázat")
    
    comparison_data = []
    for data in cities_data:
        comparison_data.append({
            '🏙️ Város': data['city'],
            '🌡️ Hőmérséklet': app.format_temperature(data['temperature']),
            '💧 Páratartalom': f"{data['humidity']}%",
            '🎯 Nyomás': f"{data.get('pressure', 'N/A')} hPa",
            '💨 Szél': f"{data.get('wind_speed', 'N/A')} m/s",
            '☁️ Leírás': data['description'].capitalize(),
            '🕐 Frissítve': app.format_time(data['timestamp'])
        })
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "🏙️ Város": st.column_config.TextColumn("Város", width="medium"),
            "🌡️ Hőmérséklet": st.column_config.TextColumn("Hőmérséklet", width="small"),
            "💧 Páratartalom": st.column_config.TextColumn("Pára", width="small"),
        }
    )

def display_settings(app):
    """Beállítások oldal"""
    st.markdown('<h1 class="main-header">⚙️ Beállítások</h1>', unsafe_allow_html=True)
    
    # API beállítások
    st.subheader("🔌 API Konfiguráció")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_api_url = st.text_input(
            "Backend URL:",
            value=app.api_url,
            help="A saját FastAPI backend címe (pl: http://localhost:8000)",
            key="api_url_input"
        )
        
        if new_api_url != app.api_url:
            app.api_url = new_api_url
            st.session_state.api_url = new_api_url
            st.success("✅ Backend URL frissítve!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        st.write("Backend állapot:")
        try:
            response = requests.get(f"{app.api_url}/health", timeout=3)
            if response.status_code == 200:
                st.success("✅ Backend elérhető")
                # Extra információ
                health_data = response.json()
                st.caption(f"Status: {health_data.get('status', 'N/A')}")
            else:
                st.error(f"❌ Backend hiba: {response.status_code}")
        except:
            st.error("❌ Backend nem elérhető")
    
    # OpenWeather API kulcs
    st.subheader("🌤️ OpenWeather API Kulcs")
    
    # Jelszó típusú mező (blur effect)
    col1= st.columns([3, 1])
    
    with col1:
        new_api_key = st.text_input(
            "API Kulcs:",
            value=app.api_key,
            type="password" if not st.session_state.show_api_key else "text",
            help="Az OpenWeatherMap API kulcsa. A kulcs biztonságosan van elrejtve.",
            key="api_key_input"
        )
        
        if new_api_key != app.api_key:
            app.api_key = new_api_key
            st.session_state.api_key = new_api_key
            st.success("✅ API kulcs frissítve!")
            time.sleep(1)
            st.rerun()
    
    # API kulcs formátuma ellenőrzése
    if st.session_state.api_key:
        st.info(f"API kulcs hossza: {len(st.session_state.api_key)} karakter")
        
        # Egyszerű formátum ellenőrzés
        if len(st.session_state.api_key) < 20:
            st.warning("⚠️ Az API kulcs túl rövidnek tűnik")
        elif len(st.session_state.api_key) > 50:
            st.warning("⚠️ Az API kulcs túl hosszúnak tűnik")
        else:
            st.success("✅ API kulcs formátuma megfelelőnek tűnik")
    
    # API kulcs tesztelése
    if st.button("🔑 API kulcs tesztelése", type="secondary"):
        if st.session_state.api_key:
            with st.spinner("API kulcs ellenőrzése..."):
                try:
                    # Teszt hívás OpenWeather API-hoz
                    test_url = f"https://api.openweathermap.org/data/2.5/weather?q=Budapest&appid={st.session_state.api_key}&units=metric"
                    response = requests.get(test_url, timeout=5)
                    
                    if response.status_code == 200:
                        st.success("✅ API kulcs érvényes!")
                        test_data = response.json()
                        st.info(f"Teszt adatok: {test_data.get('name', 'Budapest')} - {test_data['main']['temp']}°C")
                    elif response.status_code == 401:
                        st.error("❌ API kulcs érvénytelen vagy lejárt")
                    else:
                        st.error(f"❌ API hiba: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Hiba a teszt során: {e}")
        else:
            st.warning("⚠️ Nincs megadva API kulcs")
    
    # Adatbázis információk
    st.subheader("🗄️ Adatbázis információk")
    
    data = app.fetch_data("/api/cities")
    if data:
        cities = data.get('cities', [])
        st.write(f"**Városok az adatbázisban:** {len(cities)}")
        
        # Városok megjelenítése chip-ekként
        st.write(" ".join([f'<span class="city-chip">{city}</span>' for city in cities]), 
                 unsafe_allow_html=True)
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
    
    # Visszaállítás
    st.subheader("🔄 Visszaállítás")
    
    if st.button("Alapértelmezett beállítások", type="secondary"):
        st.session_state.api_url = 'http://localhost:8000'
        st.session_state.api_key = ''
        st.session_state.show_api_key = False
        st.success("✅ Beállítások visszaállítva!")
        time.sleep(1)
        st.rerun()
    
    # Konfiguráció exportálása (csak fejlesztéshez)
    with st.expander("🔧 Fejlesztői beállítások"):
        st.json({
            "api_url": st.session_state.api_url,
            "api_key_length": len(st.session_state.api_key),
            "page": st.session_state.page,
            "last_refresh": st.session_state.last_refresh.isoformat()
        })
        
        if st.button("Konfiguráció törlése", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ Konfiguráció törölve")
            time.sleep(1)
            st.rerun()

# ============================================
# 5. FŐ ALKALMAZÁS
# ============================================

def main():
    """Fő alkalmazás"""
    
    # Alkalmazás inicializálása
    app = WeatherApp()
    
    # Oldalsáv megjelenítése
    display_sidebar(app)
    
    # Oldal kiválasztása a session state alapján
    page = st.session_state.page
    
    # Oldal renderelése
    if page == 'current':
        display_current_weather(app)
    elif page == 'history':
        display_history(app)
    elif page == 'stats':
        display_statistics(app)
    elif page == 'comparison':
        display_comparison(app)
    elif page == 'settings':
        display_settings(app)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption("🌤️ Weather Dashboard v2.0 | Eszterházy Károly Katolikus Egyetem | Multi-paradigmás programozás")
    
    with col2:
        if st.button("📚 API Dokumentáció", key="api_docs"):
            import webbrowser
            webbrowser.open(f"{app.api_url}/docs")
    
    with col3:
        if st.button("🔄 Oldal frissítése", key="refresh_page"):
            st.rerun()

# ============================================
# 6. ALKALMAZÁS INDÍTÁSA
# ============================================

if __name__ == "__main__":
    main()