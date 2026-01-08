"""
🌤️ Weather Dashboard Frontend
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
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
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
        default_values = {
            'page': 'current',
            'api_url': 'http://localhost:8000',
            'api_key': '',
            'show_api_key': False,
            'last_refresh': datetime.now(),
            'selected_cities': ["Budapest", "Debrecen", "Szeged"],
            'backend_status': 'unknown',
            'api_key_status': 'unknown'
        }
        
        for key, value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
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
    
    def check_backend_status(self):
        """Backend állapot ellenőrzése"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=3)
            if response.status_code == 200:
                return "connected", response.json()
            else:
                return "error", None
        except:
            return "disconnected", None
    
    def test_api_key(self, api_key):
        """OpenWeather API kulcs tesztelése"""
        if not api_key or len(api_key) < 20:
            return "invalid", "API kulcs túl rövid"
        
        try:
            test_url = f"https://api.openweathermap.org/data/2.5/weather?q=Budapest&appid={api_key}&units=metric&lang=hu"
            response = requests.get(test_url, timeout=5)
            
            if response.status_code == 200:
                return "valid", response.json()
            elif response.status_code == 401:
                return "invalid", "API kulcs érvénytelen vagy lejárt"
            else:
                return "error", f"API hiba (kód: {response.status_code})"
        except requests.exceptions.Timeout:
            return "error", "Időtúllépés"
        except Exception as e:
            return "error", str(e)

# ============================================
# 3. OLDALSÁV (SIDEBAR)
# ============================================

def display_sidebar(app):
    """Oldalsáv megjelenítése"""
    with st.sidebar:
        # Logo és cím
        st.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <h1 style="color: #1E88E5; margin-bottom: 0;">🌤️</h1>
            <h2 style="color: #1E88E5; margin-top: 0;">Időjárás Dashboard</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigáció
        st.subheader("📍 Navigáció")
        
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
        
        # Beállítások gomb
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
        
        # Backend státusz ellenőrzése
        status, health_data = app.check_backend_status()
        if status == "connected":
            st.success("✅ Backend elérhető")
            if health_data:
                st.caption(f"Status: {health_data.get('status', 'N/A')}")
        elif status == "disconnected":
            st.error("❌ Backend nem elérhető")
        else:
            st.warning("⚠️ Backend hiba")
        
        st.caption(f"**Frissítve:** {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        # Város információk
        if st.button("🏙️ Városok", use_container_width=True, type="secondary"):
            data = app.fetch_data("/api/cities")
            if data:
                cities = data.get('cities', [])
                st.info(f"**{len(cities)} város** az adatbázisban")
            else:
                st.error("❌ Nem lehet lekérdezni a városokat")

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
        
        # Extra információk
        with st.expander("ℹ️ További információk", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🌡️ Hőmérséklet érzet:**")
                temp = data['temperature']
                if temp < 0:
                    st.write("❄️ Nagyon hideg")
                elif temp < 10:
                    st.write("🥶 Hideg")
                elif temp < 20:
                    st.write("😊 Kellemes")
                elif temp < 30:
                    st.write("😎 Meleg")
                else:
                    st.write("🔥 Nagyon meleg")
            
            with col2:
                st.write("**💨 Szélirány:**")
                wind_deg = data.get('wind_deg', 0)
                directions = ['É', 'ÉK', 'K', 'DK', 'D', 'DNy', 'Ny', 'ÉNy']
                idx = round(wind_deg / 45) % 8
                st.write(f"🧭 {directions[idx]} ({wind_deg}°)")
    
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
            ["Vonal", "Oszlop", "Pont", "Terület"],
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
        elif chart_type == "Pont":
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                mode='markers',
                name='Hőmérséklet',
                marker=dict(size=10, color=df['humidity'], colorscale='Viridis', showscale=True),
                hovertemplate='<b>%{x|%H:%M}</b><br>Hőmérséklet: %{y:.1f}°C<br>Páratartalom: %{marker.color}%<extra></extra>'
            ))
        else:  # Terület
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                mode='lines',
                name='Hőmérséklet',
                fill='tozeroy',
                fillcolor='rgba(255, 107, 107, 0.2)',
                line=dict(color='#FF6B6B', width=2),
                hovertemplate='<b>%{x|%H:%M}</b><br>Hőmérséklet: %{y:.1f}°C<extra></extra>'
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
        
        # Statisztikák
        st.subheader("📊 Statisztikai összefoglaló")
        
        if len(df) > 1:
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
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y.%m.%d %H:%M')
            display_df.columns = ['Idő', 'Hőmérséklet (°C)', 'Páratartalom (%)', 'Nyomás (hPa)', 
                                 'Szél (m/s)', 'Leírás']
            st.dataframe(display_df, use_container_width=True, height=400)
    
    else:
        st.warning(f"⚠️ Nincs elég adat {city} városhoz")
        st.info("""
        **Adatok generálása:**
        1. Várj 5 percet, hogy a scheduler gyűjtsön adatot
        2. Használd a '🔄 Frissítés' gombot az oldalsávban
        3. Nyisd meg a '📊 Statisztikák' oldalt
        
        **Gyors javítás:**
        1. Menj a Beállítások oldalra
        2. Ellenőrizd, hogy a backend fut-e
        3. Használd a manuális frissítést
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
            [1, 6, 12, 24, 48, 72, 168],
            index=3,
            format_func=lambda x: f"{x} óra" if x < 24 else f"{x//24} nap" if x % 24 == 0 else f"{x} óra",
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
            
            **📊 Mérések száma:**  
            {data['record_count']} db
            
            **🕐 Utolsó frissítés:**  
            {app.format_time(data.get('last_update', '')) if data.get('last_update') else 'N/A'}
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
            history_data = app.fetch_data("/api/weather/history", {"city": city, "limit": min(48, hours*2)})
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
        st.info("""
        **Megoldások:**
        1. Várj, hogy a scheduler gyűjtsön több adatot
        2. Használd a '🔄 Frissítés' gombot
        3. Ellenőrizd, hogy a backend fut-e
        4. Csökkentsd az időtartamot (pl. 1 óra)
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
        if len(app.cities) >= 2:
            st.info(f"**Javaslat:** {app.cities[0]} és {app.cities[1]}")
            if st.button("🔄 Automatikus kiválasztás", key="auto_select"):
                st.session_state.selected_cities = app.cities[:2]
                st.rerun()
        return
    
    # Adatok gyűjtése
    with st.spinner("Városok adatainak betöltése..."):
        cities_data = []
        failed_cities = []
        
        progress_bar = st.progress(0)
        for i, city in enumerate(selected_cities):
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
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 2. Radar diagram (opcionális, ha sok adat van)
    if len(cities_data) >= 3:
        st.subheader("🎯 Több szempont összehasonlítása")
        
        categories = ['Hőmérséklet', 'Páratartalom', 'Légnyomás']
        
        fig2 = go.Figure()
        
        for i, data in enumerate(cities_data):
            # Normalizáljuk az értékeket (0-100 skálára)
            temp_norm = (data['temperature'] + 20) * 2  # -20°C = 0, 30°C = 100
            humidity_norm = data['humidity']  # 0-100 már jó
            pressure_norm = (data.get('pressure', 1013) - 900) / 2  # 900 hPa = 0, 1100 hPa = 100
            
            values = [
                min(100, max(0, temp_norm)),
                humidity_norm,
                min(100, max(0, pressure_norm))
            ]
            
            fig2.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=data['city']
            ))
        
        fig2.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # 3. Táblázatos összehasonlítás
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

def display_settings(app):
    """Beállítások oldal - TELJESEN JAVÍTVA"""
    st.markdown('<h1 class="main-header">⚙️ Beállítások</h1>', unsafe_allow_html=True)
    
    # 1. API Konfiguráció
    st.subheader("🔌 API Konfiguráció")
    
    api_col1, api_col2 = st.columns(2)
    
    with api_col1:
        new_api_url = st.text_input(
            "Backend URL:",
            value=app.api_url,
            help="A saját FastAPI backend címe (pl: http://localhost:8000)",
            key="api_url_input"
        )
        
        if st.button("💾 URL mentése", use_container_width=True, key="save_url"):
            if new_api_url != app.api_url:
                app.api_url = new_api_url
                st.session_state.api_url = new_api_url
                st.success("✅ Backend URL frissítve!")
                time.sleep(1)
                st.rerun()
    
    with api_col2:
        st.write("**Backend állapot:**")
        try:
            response = requests.get(f"{app.api_url}/health", timeout=3)
            if response.status_code == 200:
                st.success("✅ Backend elérhető")
                health_data = response.json()
                
                col_status, col_info = st.columns(2)
                with col_status:
                    st.metric("Státusz", health_data.get('status', 'N/A'))
                with col_info:
                    st.metric("Scheduler", "Aktív" if health_data.get('scheduler') else "Inaktív")
                    
                # Extra információk
                with st.expander("Részletes információk", expanded=False):
                    st.json(health_data)
                    
            elif response.status_code == 404:
                st.warning("⚠️ Health endpoint nem található")
            else:
                st.error(f"❌ Backend hiba: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Backend nem elérhető")
        except Exception as e:
            st.error(f"❌ Hiba: {str(e)}")
    
    st.divider()
    
    # 2. OpenWeather API Kulcs
    st.subheader("🌤️ OpenWeather API Kulcs")
    
    # Létrehozunk egy segítő változót, ha nincs még
    if 'show_api_key' not in st.session_state:
        st.session_state.show_api_key = False
    
    # Két oszlop a kulcs beviteléhez
    key_col, toggle_col = st.columns([3, 1])
    
    with key_col:
        new_api_key = st.text_input(
            "API Kulcs:",
            value=app.api_key,
            type="password" if not st.session_state.show_api_key else "text",
            help="Az OpenWeatherMap API kulcsa. Regisztrálj: https://openweathermap.org/api",
            key="api_key_input",
            placeholder="Ide írd be az API kulcsod..."
        )
    
    with toggle_col:
        # Gomb a kulcs láthatóságának váltásához
        toggle_text = "👁️ Mutat" if not st.session_state.show_api_key else "🙈 Rejt"
        if st.button(toggle_text, use_container_width=True, key="toggle_key"):
            st.session_state.show_api_key = not st.session_state.show_api_key
            st.rerun()
    
    # Mentés gomb
    if st.button("💾 API kulcs mentése", use_container_width=True, key="save_api_key"):
        if new_api_key != app.api_key:
            app.api_key = new_api_key
            st.session_state.api_key = new_api_key
            st.success("✅ API kulcs frissítve!")
            time.sleep(1)
            st.rerun()
        else:
            st.info("ℹ️ API kulcs nem változott")
    
    # Kulcs információ
    if st.session_state.api_key:
        st.info(f"🔐 API kulcs hossza: **{len(st.session_state.api_key)}** karakter")
        
        # Formátum ellenőrzés
        col_check1, col_check2, col_check3 = st.columns(3)
        
        with col_check1:
            if len(st.session_state.api_key) < 20:
                st.error("❌ Túl rövid")
            else:
                st.success("✅ Megfelelő hossz")
        
        with col_check2:
            if st.session_state.api_key.startswith(('sk_', 'pk_')):
                st.success("✅ Megfelelő formátum")
            else:
                st.warning("⚠️ Nem szabványos formátum")
        
        with col_check3:
            if st.session_state.api_key == "your_api_key_here":
                st.error("❌ Alapértelmezett kulcs")
            else:
                st.success("✅ Egyedi kulcs")
    
    # Kulcs tesztelése
    st.subheader("🔑 API kulcs tesztelése")
    
    test_col1, test_col2, test_col3 = st.columns([2, 1, 1])
    
    with test_col1:
        if st.button("🧪 Kulcs tesztelése", use_container_width=True, type="primary"):
            if st.session_state.api_key:
                with st.spinner("API kulcs ellenőrzése..."):
                    status, result = app.test_api_key(st.session_state.api_key)
                    
                    if status == "valid":
                        st.success("✅ API kulcs érvényes!")
                        st.info(f"""
                        **Teszt sikeres:**
                        - Város: {result.get('name', 'Budapest')}
                        - Hőmérséklet: {result['main']['temp']}°C
                        - Leírás: {result['weather'][0]['description']}
                        """)
                    elif status == "invalid":
                        st.error(f"❌ {result}")
                    else:
                        st.error(f"❌ Hiba: {result}")
            else:
                st.warning("⚠️ Nincs megadva API kulcs")
    
    with test_col2:
        if st.button("🗑️ Kulcs törlése", use_container_width=True, type="secondary"):
            st.session_state.api_key = ''
            app.api_key = ''
            st.success("✅ API kulcs törölve!")
            time.sleep(1)
            st.rerun()
    
    with test_col3:
        if st.button("📋 Másolás", use_container_width=True, type="secondary"):
            if st.session_state.api_key:
                st.code(st.session_state.api_key, language="text")
                st.success("✅ Kulcs kimásolva")
            else:
                st.warning("⚠️ Nincs kulcs a másoláshoz")
    
    st.divider()
    
    # 3. Adatbázis információk
    st.subheader("🗄️ Adatbázis információk")
    
    data = app.fetch_data("/api/cities")
    if data:
        cities = data.get('cities', [])
        st.write(f"**Városok az adatbázisban:** {len(cities)}")
        
        if cities:
            # Városok megjelenítése chip-ekként
            cities_html = " ".join([f'<span class="city-chip">{city}</span>' for city in sorted(cities)])
            st.markdown(cities_html, unsafe_allow_html=True)
            
            # Adatbázis statisztikák
            config_data = app.fetch_data("/api/config")
            if config_data:
                col_db1, col_db2, col_db3 = st.columns(3)
                
                with col_db1:
                    st.metric("Frissítési időköz", f"{config_data.get('schedule_interval', 30)} perc")
                
                with col_db2:
                    st.metric("Alapértelmezett városok", len(config_data.get('default_cities', [])))
                
                with col_db3:
                    scheduler_status = config_data.get('scheduler_status', 'unknown')
                    status_color = "🟢" if scheduler_status == "active" else "🔴"
                    st.metric("Scheduler", f"{status_color} {scheduler_status}")
    else:
        st.warning("Nem lehet kapcsolódni az adatbázishoz")
    
    st.divider()
    
    # 4. Rendszer információk
    st.subheader("ℹ️ Rendszer információk")
    
    sys_col1, sys_col2, sys_col3 = st.columns(3)
    
    with sys_col1:
        st.metric("Frontend", "Streamlit 1.52")
        st.metric("Backend", "FastAPI")
    
    with sys_col2:
        st.metric("Adatbázis", "SQLite")
        st.metric("Python", "3.10+")
    
    with sys_col3:
        st.metric("API Provider", "OpenWeather")
        st.metric("Vizualizáció", "Plotly")
    
    st.divider()
    
    # 5. Visszaállítás
    st.subheader("🔄 Visszaállítás")
    
    reset_col1, reset_col2 = st.columns(2)
    
    with reset_col1:
        if st.button("⚙️ Alapértelmezett beállítások", use_container_width=True, type="secondary"):
            st.session_state.api_url = 'http://localhost:8000'
            st.session_state.api_key = ''
            st.session_state.show_api_key = False
            st.success("✅ Beállítások visszaállítva!")
            time.sleep(1)
            st.rerun()
    
    with reset_col2:
        if st.button("🗑️ Összes adat törlése", use_container_width=True, type="secondary"):
            st.warning("⚠️ Ez a művelet törli az összes session adatot!")
            if st.button("⚠️ Megerősítés", type="primary", key="confirm_reset"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("✅ Összes adat törölve")
                time.sleep(1)
                st.rerun()
    
    # 6. Fejlesztői beállítások
    with st.expander("🔧 Fejlesztői beállítások", expanded=False):
        config_data = {
            "api_url": st.session_state.api_url,
            "api_key_length": len(st.session_state.api_key),
            "api_key_set": bool(st.session_state.api_key),
            "page": st.session_state.page,
            "last_refresh": st.session_state.last_refresh.isoformat(),
            "selected_cities": st.session_state.selected_cities,
            "show_api_key": st.session_state.show_api_key
        }
        
        st.json(config_data)
        
        # Session state kezelés
        if st.button("📋 Session state megjelenítése", key="show_session"):
            st.write(st.session_state)
        
        # Cache törlés
        if st.button("🧹 Cache törlése", key="clear_cache_dev"):
            st.cache_data.clear()
            st.success("✅ Cache törölve")

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
    else:
        # Alapértelmezett: aktuális időjárás
        display_current_weather(app)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption("🌤️ Weather Dashboard v2.0 | Eszterházy Károly Katolikus Egyetem | Multi-paradigmás programozás")
    
    with col2:
        if st.button("📚 API Dokumentáció", key="api_docs"):
            import webbrowser
            try:
                webbrowser.open(f"{app.api_url}/docs")
                st.success("✅ Dokumentáció megnyitva")
            except:
                st.warning("⚠️ Nem sikerült megnyitni a dokumentációt")
    
    with col3:
        if st.button("🔄 Oldal frissítése", key="refresh_page"):
            st.rerun()

# ============================================
# 6. ALKALMAZÁS INDÍTÁSA
# ============================================

if __name__ == "__main__":
    main()