"""
🌤️ Weather Dashboard Frontend - 7 NAPOS ELŐREJELZÉSSEL
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

# CSS stílusok - JAVÍTVA: Szövegszínek beállítva
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
        color: white !important;  /* !important hozzáadva */
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #333333 !important;  /* !important hozzáadva */
    }
    .forecast-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        color: #333333 !important;  /* !important hozzáadva */
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
    .today-highlight {
        border: 3px solid #1E88E5 !important;
        box-shadow: 0 0 15px rgba(30, 136, 229, 0.3) !important;
    }
    /* Gyors előrejelzés kártya */
    .quick-forecast-card {
        background: #f8f9fa !important;
        border-radius: 10px !important;
        padding: 15px !important;
        text-align: center !important;
        color: #333333 !important;
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
            'forecast_cache': {}
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
    
    def get_weekday(self, date_str):
        """Dátum szöveggé konvertálása (hét napja)"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            weekdays = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]
            today = datetime.now().date()
            
            if date_obj.date() == today:
                return "Ma"
            elif date_obj.date() == today + timedelta(days=1):
                return "Holnap"
            else:
                return weekdays[date_obj.weekday()]
        except:
            return date_str
    
    def format_date(self, date_str):
        """Dátum formázása"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%m.%d")
        except:
            return date_str

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
        
        col5, col6 = st.columns(2)
        
        with col5:
            if st.button("🌤️ 7 Napos", use_container_width=True,
                        type="primary" if st.session_state.page == 'forecast' else "secondary"):
                st.session_state.page = 'forecast'
                st.rerun()
        
        with col6:
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
        if st.button("🌤️ Előrejelzés", use_container_width=True, key="goto_forecast"):
            st.session_state.page = 'forecast'
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
                <h1 style='font-size: 4.5rem; margin: 0; color: white !important;'>{app.format_temperature(data['temperature'])}</h1>
                <h2 style='margin-top: 0; color: white !important;'>{city}</h2>
                <p style='font-size: 1.8rem; margin-bottom: 5px; color: white !important;'>{data['description'].capitalize()}</p>
                <p style='opacity: 0.9; color: white !important;'>Utolsó frissítés: {app.format_time(data['timestamp'])}</p>
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
                <div style='background: {color}20; border-radius: 12px; padding: 20px; text-align: center; color: #333333 !important;'>
                    <div style='font-size: 1.2rem; color: {color}; font-weight: bold;'>{label}</div>
                    <div style='font-size: 1.8rem; font-weight: bold; color: #333333 !important;'>{value}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Gyors előrejelzés - JAVÍTVA: Szöveg szín beállítva
        with st.expander("📅 Gyors 3 napos előrejelzés", expanded=False):
            forecast_data = app.fetch_data("/api/forecast", {"city": city, "days": 3})
            if forecast_data and forecast_data.get('forecasts'):
                forecast_cols = st.columns(3)
                for idx, forecast in enumerate(forecast_data['forecasts']):
                    with forecast_cols[idx]:
                        weekday = app.get_weekday(forecast['date'])
                        icon_url = app.get_weather_icon(forecast['icon'])
                        
                        st.markdown(f"""
                        <div class='quick-forecast-card'>
                            <div style='font-weight: bold; color: #333333 !important;'>{weekday}</div>
                            <img src='{icon_url}' style='width: 60px; height: 60px;'>
                            <div style='font-size: 1.2rem; font-weight: bold; color: #333333 !important;'>{forecast['day_temp']}°C</div>
                            <div style='font-size: 0.9rem; color: #333333 !important;'>{forecast['description']}</div>
                        </div>
                        """, unsafe_allow_html=True)
    
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

def display_forecast_card(app, forecast, is_today=False):
    """Egy nap előrejelzésének megjelenítése kártyán - STREAMLIT KOMPONENSEKKEL"""
    weekday = app.get_weekday(forecast['date'])
    date_formatted = app.format_date(forecast['date'])
    
    # Kártya stílus
    card_class = "weather-card" if is_today else "forecast-card"
    
    # Ikon URL
    icon_url = f"https://openweathermap.org/img/wn/{forecast['icon']}@2x.png"
    
    # Csapadék valószínűség kezelése
    pop_value = forecast.get('pop', 0)
    
    # Biztonságos értékek kezelése
    try:
        pop_value = float(pop_value)
    except (ValueError, TypeError):
        pop_value = 0
    
    # Csapadék ikon és szín
    if pop_value > 70:
        pop_icon = "🌧️"
        pop_color = "#667eea"
    elif pop_value > 40:
        pop_icon = "🌦️"
        pop_color = "#95E1D3"
    elif pop_value > 10:
        pop_icon = "⛅"
        pop_color = "#FFD166"
    else:
        pop_icon = "☀️"
        pop_color = "#FF6B6B"
    
    # Hőmérséklet értékek formázása
    day_temp = forecast.get('day_temp', 0)
    night_temp = forecast.get('night_temp', 0)
    max_temp = forecast.get('max_temp', 0)
    min_temp = forecast.get('min_temp', 0)
    humidity = forecast.get('humidity', 0)
    description = forecast.get('description', '')
    
    # Streamlit komponensekkel építjük fel a kártyát
    with st.container():
        # A külső div a CSS osztállyal
        st.markdown(f'<div class="{card_class} {"today-highlight" if is_today else ""}">', unsafe_allow_html=True)
        
        # Fejléc: Nap és dátum
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.markdown(f"**{weekday}**")
        with col_header2:
            st.caption(date_formatted)
        
        # Ikon és főhőmérséklet középre
        col_center = st.columns([1])
        with col_center[0]:
            st.image(icon_url, width=80)
            st.markdown(f"### {day_temp}°C")
            st.markdown(f"*{description.capitalize()}*")
        
        # Részletek
        st.divider()
        
        col_details1, col_details2 = st.columns(2)
        with col_details1:
            st.metric("🌙 Éjszaka", f"{night_temp}°C")
            st.metric("📈 Max", f"{max_temp}°C")
        with col_details2:
            st.metric("📉 Min", f"{min_temp}°C")
            st.metric("💧 Pára", f"{humidity}%")
        
        # Csapadék
        st.markdown(f'<div style="text-align: center; color: {pop_color}; font-weight: bold;">{pop_icon} Csapadék: {pop_value}%</div>', unsafe_allow_html=True)
        
        # Bezárjuk a külső div-et
        st.markdown('</div>', unsafe_allow_html=True)

def display_forecast(app):
    """7 napos időjárás előrejelzés megjelenítése"""
    st.markdown('<h1 class="main-header">🌤️ 7 Napos Időjárás Előrejelzés</h1>', unsafe_allow_html=True)
    
    # Város választó
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        city = st.selectbox(
            "Válassz várost:",
            app.cities,
            index=0,
            key="forecast_city_select"
        )
    
    with col2:
        days = st.selectbox(
            "Napok:",
            [3, 5, 7],
            index=2,
            key="forecast_days"
        )
    
    with col3:
        if st.button("🔄 Frissítés", use_container_width=True, key="refresh_forecast"):
            if 'forecast_cache' in st.session_state:
                del st.session_state.forecast_cache
            st.rerun()
    
    # Adatok lekérése
    with st.spinner(f"{days} napos előrejelzés betöltése..."):
        # Cache használata
        cache_key = f"forecast_{city}_{days}"
        
        if 'forecast_cache' not in st.session_state:
            st.session_state.forecast_cache = {}
        
        if cache_key not in st.session_state.forecast_cache:
            data = app.fetch_data("/api/forecast", {"city": city, "days": days})
            if data:
                st.session_state.forecast_cache[cache_key] = data
            else:
                data = None
        else:
            data = st.session_state.forecast_cache[cache_key]
    
    if data and data.get('forecasts'):
        forecasts = data['forecasts']
        actual_days = len(forecasts)
        
        # Összefoglaló kártyák
        st.subheader(f"📅 {actual_days} napos előrejelzés - {data['city']}")
        
        # Ha kevesebb napot kaptunk vissza, mint amennyit kértünk
        if actual_days < days:
            st.info(f"ℹ️ Az API {actual_days} napos előrejelzést adott vissza")
        
        # Napok megjelenítése kártyákban - EGYSZERŰBB MÓDSZER
        # Mindig csak annyi napot jelenítünk meg, amennyi van
        if actual_days <= 3:
            cols = st.columns(actual_days)
            for idx, forecast in enumerate(forecasts):
                with cols[idx]:
                    display_forecast_card(app, forecast, idx == 0)
        elif actual_days <= 6:
            # Két sorban jelenítjük meg
            first_half = actual_days // 2
            second_half = actual_days - first_half
            
            # Első sor
            cols1 = st.columns(first_half)
            for idx in range(first_half):
                with cols1[idx]:
                    display_forecast_card(app, forecasts[idx], idx == 0)
            
            # Második sor
            if second_half > 0:
                st.write("")  # Üres sor
                cols2 = st.columns(second_half)
                for idx in range(first_half, actual_days):
                    with cols2[idx - first_half]:
                        display_forecast_card(app, forecasts[idx], False)
        else:
            # Három sorban jelenítjük meg (max 7 nap)
            rows = [3, 2, 2]  # Az első sor 3, második 2, harmadik 2 kártya
            
            start_idx = 0
            for row_count in rows:
                if start_idx >= actual_days:
                    break
                    
                cols = st.columns(min(row_count, actual_days - start_idx))
                for col_idx in range(min(row_count, actual_days - start_idx)):
                    idx = start_idx + col_idx
                    with cols[col_idx]:
                        display_forecast_card(app, forecasts[idx], idx == 0)
                
                start_idx += row_count
                if start_idx < actual_days:
                    st.write("")  # Üres sor sorok között
        
        st.divider()
        
        # Részletes diagramok (opcionális)
        if actual_days >= 3:
            st.subheader("📈 Hőmérséklet trend")
            
            dates = [app.get_weekday(f['date']) for f in forecasts]
            day_temps = [f['day_temp'] for f in forecasts]
            night_temps = [f['night_temp'] for f in forecasts]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=day_temps,
                mode='lines+markers',
                name='Nappali',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=10, color='#FF6B6B')
            ))
            fig.add_trace(go.Scatter(
                x=dates,
                y=night_temps,
                mode='lines+markers',
                name='Éjszakai',
                line=dict(color='#45B7D1', width=3, dash='dash'),
                marker=dict(size=8, color='#45B7D1')
            ))
            
            fig.update_layout(
                title=f'{data["city"]} - Hőmérséklet előrejelzés',
                xaxis_title='Nap',
                yaxis_title='Hőmérséklet (°C)',
                height=400,
                template='plotly_white',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Részletes táblázat
        st.subheader("📋 Részletes előrejelzés")
        
        forecast_data = []
        for forecast in forecasts:
            forecast_data.append({
                '📅 Nap': app.get_weekday(forecast['date']),
                '📆 Dátum': app.format_date(forecast['date']),
                '🌡️ Nappali': f"{forecast['day_temp']}°C",
                '🌙 Éjszakai': f"{forecast['night_temp']}°C",
                '📈 Max': f"{forecast['max_temp']}°C",
                '📉 Min': f"{forecast['min_temp']}°C",
                '💧 Pára': f"{forecast['humidity']}%",
                '🌧️ Csapadék': f"{forecast['pop']}%",
                '💨 Szél': f"{forecast['wind_speed']} m/s",
                '🎯 Nyomás': f"{forecast['pressure']} hPa",
                '☁️ Időjárás': forecast['description'].capitalize()
            })
        
        df = pd.DataFrame(forecast_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "📅 Nap": st.column_config.TextColumn("Nap", width="small"),
                "📆 Dátum": st.column_config.TextColumn("Dátum", width="small"),
                "🌡️ Nappali": st.column_config.TextColumn("Nappali", width="small"),
                "🌙 Éjszakai": st.column_config.TextColumn("Éjszaka", width="small"),
                "📈 Max": st.column_config.TextColumn("Max", width="small"),
                "📉 Min": st.column_config.TextColumn("Min", width="small"),
                "💧 Pára": st.column_config.TextColumn("Pára", width="small"),
                "🌧️ Csapadék": st.column_config.TextColumn("Csap.", width="small"),
                "💨 Szél": st.column_config.TextColumn("Szél", width="small"),
                "🎯 Nyomás": st.column_config.TextColumn("Nyomás", width="small"),
                "☁️ Időjárás": st.column_config.TextColumn("Időjárás", width="medium"),
            }
        )
        
        # Exportálás lehetősége
        if st.button("💾 Exportálás CSV-ként", use_container_width=True):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV letöltése",
                data=csv,
                file_name=f"elorejelzes_{city}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    else:
        st.error("❌ Nem sikerült betölteni az előrejelzést")
        st.info("""
        **Lehetséges okok:**
        1. OpenWeather API kulcs nincs beállítva
        2. Nincs internetkapcsolat
        3. A város nem található
        
        **Megoldások:**
        1. Ellenőrizd az API kulcsot a Beállítások oldalon
        2. Ellenőrizd az internetkapcsolatot
        3. Próbálj másik várost
        4. Ellenőrizd, hogy a backend fut-e
        """)

def display_settings(app):
    """Beállítások oldal"""
    st.markdown('<h1 class="main-header">⚙️ Beállítások</h1>', unsafe_allow_html=True)
    
    # API konfiguráció
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
                health_data = response.json()
                st.caption(f"Status: {health_data.get('status', 'N/A')}")
            else:
                st.error(f"❌ Backend hiba: {response.status_code}")
        except:
            st.error("❌ Backend nem elérhető")
    
    st.divider()
    
    # Adatbázis információk
    st.subheader("🗄️ Adatbázis információk")
    
    data = app.fetch_data("/api/cities")
    if data:
        cities = data.get('cities', [])
        st.write(f"**Városok az adatbázisban:** {len(cities)}")
        
        if cities:
            cities_html = " ".join([f'<span class="city-chip">{city}</span>' for city in sorted(cities)])
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
    
    # Visszaállítás
    st.subheader("🔄 Visszaállítás")
    
    if st.button("Alapértelmezett beállítások", type="secondary"):
        st.session_state.api_url = 'http://localhost:8000'
        st.session_state.api_key = ''
        st.session_state.show_api_key = False
        st.success("✅ Beállítások visszaállítva!")
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
    elif page == 'forecast':
        display_forecast(app)
    elif page == 'settings':
        display_settings(app)
    else:
        display_current_weather(app)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption("🌤️ Weather Dashboard v2.1 | Eszterházy Károly Katolikus Egyetem | Multi-paradigmás programozás")
    
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