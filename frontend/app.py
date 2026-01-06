"""Streamlit frontend alkalmazás"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Optional

# Konfiguráció
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
CITIES = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr", "Miskolc", "Nyíregyháza"]

# Oldal konfiguráció
st.set_page_config(
    page_title="🌤️ Időjárás Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# CSS stílusok
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Helper függvények
def kelvin_to_celsius(kelvin):
    """Kelvin átváltása Celsiusra"""
    return kelvin - 273.15

def format_temp(temp):
    """Hőmérséklet formázása"""
    return f"{temp:.1f}°C"

def get_weather_icon(icon_code):
    """Időjárás ikon URL"""
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

def call_api(endpoint, params=None):
    """API hívás"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Hiba az API hívás során: {e}")
        return None

# Fő alkalmazás
def main():
    # Fejléc
    st.markdown('<h1 class="main-header">🌤️ Időjárás Dashboard</h1>', unsafe_allow_html=True)
    
    # Oldalsáv
    with st.sidebar:
        st.header("⚙️ Beállítások")
        selected_city = st.selectbox("Város kiválasztása", CITIES, index=0)
        
        st.header("📊 Nézetek")
        view_option = st.radio(
            "Válassz nézetet:",
            ["Aktuális időjárás", "Előzmények", "Összehasonlítás", "Statisztikák"]
        )
        
        if st.button("🔄 Adatok frissítése"):
            st.rerun()
        
        st.divider()
        st.markdown("---")
        st.caption(f"Backend: {BACKEND_URL}")
        st.caption(f"Utolsó frissítés: {datetime.now().strftime('%H:%M:%S')}")
    
    # Fő tartalom
    if view_option == "Aktuális időjárás":
        show_current_weather(selected_city)
    elif view_option == "Előzmények":
        show_history(selected_city)
    elif view_option == "Összehasonlítás":
        show_comparison()
    elif view_option == "Statisztikák":
        show_statistics(selected_city)

def show_current_weather(city):
    """Aktuális időjárás megjelenítése"""
    st.header(f"Aktuális időjárás - {city}")
    
    # API hívás
    data = call_api("/api/weather/current", {"city": city})
    
    if data:
        # Kártya elrendezés
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🌡️ Hőmérséklet", format_temp(data["temperature"]))
            st.metric("💨 Szél", f"{data['wind_speed']} m/s")
        
        with col2:
            st.metric("💧 Páratartalom", f"{data['humidity']}%")
            st.metric("📊 Légnyomás", f"{data['pressure']} hPa")
        
        with col3:
            st.metric("🌡️ Hőérzet", format_temp(data["feels_like"]))
            st.metric("🧭 Szélirány", data.get("wind_direction", "N/A"))
        
        # Leírás
        st.markdown(f"### {data['description'].title()}")
        
        if data.get("icon"):
            st.image(get_weather_icon(data["icon"]), width=100)
        
        # Időbélyeg
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        st.caption(f"Adatok frissítve: {timestamp.strftime('%Y.%m.%d %H:%M:%S')}")

def show_history(city):
    """Előzmények megjelenítése"""
    st.header(f"Időjárás előzmények - {city}")
    
    # Beállítások
    col1, col2 = st.columns(2)
    with col1:
        limit = st.slider("Rekordok száma", 5, 50, 20)
    
    # API hívás
    data = call_api("/api/weather/history", {"city": city, "limit": limit})
    
    if data:
        # DataFrame konvertálás
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        
        # Diagramok
        fig = go.Figure()
        
        # Hőmérséklet diagram
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["temperature"],
            mode="lines+markers",
            name="Hőmérséklet (°C)",
            line=dict(color="firebrick", width=2)
        ))
        
        # Páratartalom diagram
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["humidity"],
            mode="lines",
            name="Páratartalom (%)",
            yaxis="y2",
            line=dict(color="royalblue", width=2)
        ))
        
        # Layout
        fig.update_layout(
            title=f"Időjárás trendek - {city}",
            xaxis_title="Idő",
            yaxis_title="Hőmérséklet (°C)",
            yaxis2=dict(
                title="Páratartalom (%)",
                overlaying="y",
                side="right"
            ),
            hovermode="x unified",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Táblázat
        with st.expander("Részletes adatok"):
            display_df = df[["timestamp", "temperature", "humidity", "pressure", "wind_speed", "description"]].copy()
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%m.%d %H:%M")
            st.dataframe(display_df, use_container_width=True)

def show_comparison():
    """Több város összehasonlítása"""
    st.header("🏙️ Városok összehasonlítása")
    
    # Városok kiválasztása
    selected_cities = st.multiselect(
        "Városok kiválasztása összehasonlításhoz",
        CITIES,
        default=CITIES[:3]
    )
    
    if not selected_cities:
        st.warning("Válassz legalább egy várost!")
        return
    
    # API hívás
    cities_param = ",".join(selected_cities)
    data = call_api("/api/weather/multiple", {"cities": cities_param})
    
    if data and "cities" in data:
        weather_data = data["cities"]
        
        # Kártyák létrehozása
        cols = st.columns(len(weather_data))
        
        for idx, weather in enumerate(weather_data):
            with cols[idx]:
                with st.container():
                    st.markdown(f"""
                    <div class='weather-card'>
                        <h3>{weather['city']}</h3>
                        <h2>{format_temp(weather['temperature'])}</h2>
                        <p>{weather['description'].title()}</p>
                        <p>💧 {weather['humidity']}%</p>
                        <p>💨 {weather['wind_speed']} m/s</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Összehasonlító diagram
        st.subheader("Hőmérséklet összehasonlítás")
        
        cities = [w["city"] for w in weather_data]
        temps = [w["temperature"] for w in weather_data]
        
        fig = go.Figure(data=[
            go.Bar(x=cities, y=temps, marker_color='lightsalmon')
        ])
        
        fig.update_layout(
            title="Hőmérséklet összehasonlítás",
            xaxis_title="Városok",
            yaxis_title="Hőmérséklet (°C)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_statistics(city):
    """Statisztikák megjelenítése"""
    st.header(f"📈 Statisztikák - {city}")
    
    # Időintervallum
    hours = st.slider("Elemzés időtartama (óra)", 1, 168, 24)
    
    # API hívás
    data = call_api("/api/weather/stats", {"city": city, "hours": hours})
    
    if data:
        # Metrikák
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Átlaghőmérséklet", format_temp(data["avg_temperature"]))
        
        with col2:
            st.metric("Minimum hőmérséklet", format_temp(data["min_temperature"]))
        
        with col3:
            st.metric("Maximum hőmérséklet", format_temp(data["max_temperature"]))
        
        with col4:
            st.metric("Átlag páratartalom", f"{data['avg_humidity']}%")
        
        # További információk
        st.info(f"""
        **Elemzés részletei:**
        - Város: {data['city']}
        - Időtartam: utolsó {hours} óra
        - Rekordok száma: {data['record_count']}
        - Utolsó frissítés: {data['last_update']}
        """)

if __name__ == "__main__":
    main()