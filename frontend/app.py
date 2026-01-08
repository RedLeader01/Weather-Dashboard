"""
🌤️ Weather Dashboard Frontend - JAVÍTOTT Oldalváltással
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import webbrowser

# ============================================
# 1. KONFIGURÁCIÓ
# ============================================

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
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 25px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 2. SESSION STATE KEZELÉS
# ============================================

# Session state inicializálása
if 'page' not in st.session_state:
    st.session_state.page = 'current'
if 'api_url' not in st.session_state:
    st.session_state.api_url = 'http://localhost:8000'
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# ============================================
# 3. HELPER FÜGGVÉNYEK
# ============================================

def fetch_data(endpoint, params=None):
    """API hívás"""
    try:
        url = f"{st.session_state.api_url}{endpoint}"
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def format_temp(temp):
    """Hőmérséklet formázása"""
    return f"{temp:.1f}°C"

def format_time(timestamp_str):
    """Idő formázása"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%H:%M")
    except:
        return timestamp_str

def get_weather_icon(icon_code):
    """Időjárás ikon"""
    if icon_code:
        return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    return None

# ============================================
# 4. OLDALSÁV
# ============================================

def render_sidebar():
    """Oldalsáv renderelése"""
    with st.sidebar:
        st.title("🌤️ Időjárás")
        
        # Navigációs gombok - EGYSZERŰ GOMBOKKAL
        st.subheader("Navigáció")
        
        # Aktuális gomb
        if st.button("🏠 Aktuális időjárás", use_container_width=True):
            st.session_state.page = 'current'
            st.rerun()
        
        # Előzmények gomb
        if st.button("📈 Előzmények", use_container_width=True):
            st.session_state.page = 'history'
            st.rerun()
        
        # Statisztikák gomb
        if st.button("📊 Statisztikák", use_container_width=True):
            st.session_state.page = 'stats'
            st.rerun()
        
        # Összehasonlítás gomb
        if st.button("🏙️ Összehasonlítás", use_container_width=True):
            st.session_state.page = 'comparison'
            st.rerun()
        
        # Beállítások gomb
        if st.button("⚙️ Beállítások", use_container_width=True):
            st.session_state.page = 'settings'
            st.rerun()
        
        st.divider()
        
        # API beállítások
        st.subheader("API Beállítások")
        new_api_url = st.text_input(
            "Backend URL:",
            value=st.session_state.api_url
        )
        
        if new_api_url != st.session_state.api_url:
            st.session_state.api_url = new_api_url
            st.rerun()
        
        # API teszt
        if st.button("🔗 API teszt", use_container_width=True):
            try:
                response = requests.get(f"{new_api_url}/health", timeout=3)
                if response.status_code == 200:
                    st.success("✅ API elérhető")
                else:
                    st.error(f"❌ API hiba: {response.status_code}")
            except:
                st.error("❌ API nem elérhető")
        
        st.divider()
        
        # Manuális frissítés
        if st.button("🔄 Adatok frissítése", use_container_width=True, type="secondary"):
            response = fetch_data("/api/refresh")
            if response:
                st.success("✅ Adatok frissítve")
            else:
                st.error("❌ Frissítés sikertelen")
            time.sleep(1)
            st.rerun()
        
        # Információk
        st.caption(f"Backend: {st.session_state.api_url}")
        st.caption(f"Utolsó frissítés: {st.session_state.last_refresh.strftime('%H:%M:%S')}")

# ============================================
# 5. OLDALAK
# ============================================

def render_current_weather():
    """Aktuális időjárás oldal"""
    st.markdown('<h1 class="main-header">🌤️ Aktuális Időjárás</h1>', unsafe_allow_html=True)
    
    # Város választó
    cities = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr", "Miskolc"]
    city = st.selectbox("Válassz várost:", cities)
    
    # Adatok lekérése
    data = fetch_data("/api/weather", {"city": city})
    
    if data:
        # Fő kártya
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div class='weather-card'>
                <h1 style='font-size: 4rem; margin: 0;'>{format_temp(data['temperature'])}</h1>
                <h2 style='margin-top: 0;'>{city}</h2>
                <p style='font-size: 1.5rem;'>{data['description'].capitalize()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if data.get('icon'):
                icon_url = get_weather_icon(data['icon'])
                st.image(icon_url, width=150)
        
        # Metrikák
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💧 Páratartalom", f"{data['humidity']}%")
        
        with col2:
            st.metric("🎯 Légnyomás", f"{data.get('pressure', 'N/A')} hPa")
        
        with col3:
            st.metric("💨 Szél", f"{data.get('wind_speed', 'N/A')} m/s")
        
        with col4:
            st.metric("🕐 Frissítve", format_time(data['timestamp']))
    
    else:
        st.error("❌ Nem sikerült betölteni az adatokat")

def render_history():
    """Előzmények oldal"""
    st.markdown('<h1 class="main-header">📈 Időjárás Előzmények</h1>', unsafe_allow_html=True)
    
    # Beállítások
    col1, col2 = st.columns(2)
    
    with col1:
        cities = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr"]
        city = st.selectbox("Város:", cities, key="history_city")
    
    with col2:
        limit = st.slider("Rekordok száma:", 5, 50, 20, key="history_limit")
    
    # Adatok lekérése
    data = fetch_data("/api/weather/history", {"city": city, "limit": limit})
    
    if data and len(data) > 0:
        # DataFrame
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Diagram
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['temperature'],
            mode='lines+markers',
            name='Hőmérséklet (°C)',
            line=dict(color='#FF6B6B', width=3)
        ))
        
        fig.update_layout(
            title=f'{city} - Időjárás trend',
            xaxis_title='Idő',
            yaxis_title='Hőmérséklet (°C)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Táblázat
        with st.expander("📋 Részletes adatok"):
            display_df = df[['timestamp', 'temperature', 'humidity', 'description']].copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%m.%d %H:%M')
            st.dataframe(display_df, use_container_width=True)
    
    else:
        st.warning("⚠️ Nincs elég adat az előzményekhez")
        st.info("""
        **Mit tegyél:**
        1. Várj 5 percet, hogy a scheduler gyűjtsön adatot
        2. Nyomd meg a "🔄 Adatok frissítése" gombot az oldalsávban
        3. Ellenőrizd, hogy a backend fut-e
        """)

def render_statistics():
    """Statisztikák oldal"""
    st.markdown('<h1 class="main-header">📊 Időjárás Statisztikák</h1>', unsafe_allow_html=True)
    
    # Beállítások
    col1, col2 = st.columns(2)
    
    with col1:
        cities = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr"]
        city = st.selectbox("Város:", cities, key="stats_city")
    
    with col2:
        hours = st.selectbox(
            "Időtartam:",
            [6, 12, 24, 48, 72],
            index=2,
            format_func=lambda x: f"{x} óra",
            key="stats_hours"
        )
    
    # Adatok lekérése
    data = fetch_data("/api/weather/stats", {"city": city, "hours": hours})
    
    if data:
        # Metrikák
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 Átlag", format_temp(data['avg_temperature']))
        
        with col2:
            st.metric("📉 Minimum", format_temp(data['min_temperature']))
        
        with col3:
            st.metric("📈 Maximum", format_temp(data['max_temperature']))
        
        with col4:
            st.metric("🔢 Mérések", data['record_count'])
        
        # Infobox
        st.info(f"""
        **Statisztikai információk:**
        
        - **Város:** {data['city']}
        - **Időtartam:** utolsó {hours} óra
        - **Hőmérséklet tartomány:** {format_temp(data['min_temperature'])} - {format_temp(data['max_temperature'])}
        - **Átlag páratartalom:** {data['avg_humidity']:.1f}%
        - **Utolsó frissítés:** {format_time(data.get('last_update', ''))}
        """)
        
        # Diagram
        if data['record_count'] > 1:
            fig = go.Figure(data=[
                go.Bar(
                    x=['Átlag', 'Minimum', 'Maximum'],
                    y=[data['avg_temperature'], data['min_temperature'], data['max_temperature']],
                    marker_color=['#4ECDC4', '#FF6B6B', '#45B7D1']
                )
            ])
            
            fig.update_layout(
                title='Hőmérséklet statisztikák',
                yaxis_title='Hőmérséklet (°C)',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("❌ Nincs elég adat a statisztikákhoz")

def render_comparison():
    """Összehasonlítás oldal"""
    st.markdown('<h1 class="main-header">🏙️ Városok Összehasonlítása</h1>', unsafe_allow_html=True)
    
    # Városok kiválasztása
    all_cities = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr"]
    
    selected_cities = st.multiselect(
        "Válassz városokat:",
        all_cities,
        default=["Budapest", "Debrecen", "Szeged"]
    )
    
    if len(selected_cities) < 2:
        st.warning("⚠️ Válassz legalább 2 várost!")
        return
    
    # Adatok gyűjtése
    cities_data = []
    
    for city in selected_cities:
        data = fetch_data("/api/weather", {"city": city})
        if data:
            cities_data.append(data)
    
    if len(cities_data) < 2:
        st.error("❌ Nem sikerült adatot szerezni a városokhoz")
        return
    
    # Diagram
    fig = go.Figure(data=[
        go.Bar(
            x=[d['city'] for d in cities_data],
            y=[d['temperature'] for d in cities_data],
            text=[format_temp(d['temperature']) for d in cities_data],
            textposition='auto',
            marker_color='#95E1D3'
        )
    ])
    
    fig.update_layout(
        title='Városok hőmérséklet összehasonlítása',
        yaxis_title='Hőmérséklet (°C)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Táblázat
    st.subheader("📋 Összehasonlító táblázat")
    
    comparison_data = []
    for data in cities_data:
        comparison_data.append({
            'Város': data['city'],
            'Hőmérséklet (°C)': format_temp(data['temperature']),
            'Páratartalom (%)': data['humidity'],
            'Leírás': data['description'].capitalize(),
            'Frissítve': format_time(data['timestamp'])
        })
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)

def render_settings():
    """Beállítások oldal"""
    st.markdown('<h1 class="main-header">⚙️ Beállítások</h1>', unsafe_allow_html=True)
    
    # API beállítások
    st.subheader("🔌 API Konfiguráció")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_api_url = st.text_input(
            "Backend URL:",
            value=st.session_state.api_url
        )
        
        if new_api_url != st.session_state.api_url:
            st.session_state.api_url = new_api_url
            st.success("✅ API URL frissítve!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        st.write("API állapot:")
        try:
            response = requests.get(f"{st.session_state.api_url}/health", timeout=3)
            if response.status_code == 200:
                st.success("✅ API elérhető")
            else:
                st.error(f"❌ API hiba: {response.status_code}")
        except:
            st.error("❌ API nem elérhető")
    
    # Adatbázis információk
    st.subheader("🗄️ Adatbázis információk")
    
    data = fetch_data("/api/cities")
    if data:
        cities = data.get('cities', [])
        st.write(f"**Városok az adatbázisban:** {len(cities)}")
        st.write(", ".join(cities))
    
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
        st.success("✅ Beállítások visszaállítva!")
        time.sleep(1)
        st.rerun()

# ============================================
# 6. FŐ ALKALMAZÁS
# ============================================

def main():
    """Fő alkalmazás"""
    
    # Oldalsáv renderelése
    render_sidebar()
    
    # Oldal kiválasztása a session state alapján
    page = st.session_state.page
    
    # Oldal renderelése
    if page == 'current':
        render_current_weather()
    elif page == 'history':
        render_history()
    elif page == 'stats':
        render_statistics()
    elif page == 'comparison':
        render_comparison()
    elif page == 'settings':
        render_settings()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption("🌤️ Weather Dashboard v2.0 | Multi-paradigmás programozás")
    
    with col2:
        if st.button("📚 API Dokumentáció", key="api_docs"):
            webbrowser.open(f"{st.session_state.api_url}/docs")
    
    with col3:
        if st.button("🔄 Oldal frissítése", key="refresh_page"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()

# ============================================
# 7. INDÍTÁS
# ============================================

if __name__ == "__main__":
    main()