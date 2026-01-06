"""
🌤️ Időjárás Dashboard - Streamlit Frontend
Egyszerű, de szép felhasználói felület
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Konfiguráció
st.set_page_config(
    page_title="Időjárás Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# Stílusok
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        padding: 1rem;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
    }
    .metric-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# API URL - localhost fejlesztéshez, deploy után változtatni
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

class WeatherApp:
    """Időjárás alkalmazás osztály (OOP)"""
    
    def __init__(self):
        self.cities = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr", "Miskolc"]
    
    def fetch_data(self, endpoint, params=None):
        """API adatok lekérése"""
        try:
            url = f"{API_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Hiba: {e}")
        return None
    
    def display_current_weather(self):
        """Aktuális időjárás megjelenítése"""
        st.markdown('<h2 class="main-header">🌤️ Aktuális Időjárás</h2>', unsafe_allow_html=True)
        
        # Város választó
        col1, col2 = st.columns([3, 1])
        with col1:
            city = st.selectbox("Válassz várost:", self.cities, key="current_city")
        
        with col2:
            if st.button("🔄 Frissítés", use_container_width=True):
                st.rerun()
        
        # Adatok lekérése
        data = self.fetch_data("/api/weather", {"city": city})
        
        if data:
            # Fő információ
            st.markdown(f"""
            <div class='weather-card'>
                <h2>{city}</h2>
                <h1>{data['temperature']:.1f}°C</h1>
                <p style='font-size: 1.2em;'>{data['description'].capitalize()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrikák
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💧 Páratartalom", f"{data['humidity']}%")
            with col2:
                st.metric("📍 Város", data['city'])
            with col3:
                dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                st.metric("🕐 Frissítve", dt.strftime("%H:%M"))
    
    def display_history(self):
        """Előzmények diagrammal"""
        st.markdown('<h2 class="main-header">📈 Időjárás Előzmények</h2>', unsafe_allow_html=True)
        
        city = st.selectbox("Válassz várost:", self.cities, key="history_city")
        limit = st.slider("Rekordok száma:", 5, 50, 20)
        
        data = self.fetch_data("/api/weather/history", {"city": city, "limit": limit})
        
        if data and len(data) > 0:
            # DataFrame készítése
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
                line=dict(color='firebrick', width=2)
            ))
            
            fig.update_layout(
                title=f'{city} időjárás trendje',
                xaxis_title='Idő',
                yaxis_title='Hőmérséklet (°C)',
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Táblázat
            with st.expander("📋 Részletes adatok"):
                st.dataframe(
                    df[['timestamp', 'temperature', 'humidity', 'description']],
                    use_container_width=True
                )
    
    def display_stats(self):
        """Statisztikák"""
        st.markdown('<h2 class="main-header">📊 Statisztikák</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            city = st.selectbox("Válassz várost:", self.cities, key="stats_city")
        with col2:
            hours = st.slider("Időtartam (óra):", 1, 168, 24)
        
        data = self.fetch_data("/api/weather/stats", {"city": city, "hours": hours})
        
        if data:
            # Metrika kártyák
            cols = st.columns(4)
            with cols[0]:
                st.metric("Átlaghőmérséklet", f"{data['avg_temperature']:.1f}°C")
            with cols[1]:
                st.metric("Minimum", f"{data['min_temperature']:.1f}°C")
            with cols[2]:
                st.metric("Maximum", f"{data['max_temperature']:.1f}°C")
            with cols[3]:
                st.metric("Mérések", data['record_count'])
            
            # Infobox
            st.info(f"""
            **Statisztika részletei:**
            - Város: {data['city']}
            - Elemzett időszak: utolsó {hours} óra
            - Összes mérés: {data['record_count']}
            - Hőmérséklet tartomány: {data['min_temperature']:.1f}°C - {data['max_temperature']:.1f}°C
            """)
    
    def display_comparison(self):
        """Városok összehasonlítása"""
        st.markdown('<h2 class="main-header">🏙️ Városok Összehasonlítása</h2>', unsafe_allow_html=True)
        
        selected_cities = st.multiselect(
            "Válassz városokat:",
            self.cities,
            default=self.cities[:3]
        )
        
        if len(selected_cities) >= 2:
            # Adatok gyűjtése
            cities_data = []
            temps = []
            
            for city in selected_cities:
                data = self.fetch_data("/api/weather", {"city": city})
                if data:
                    cities_data.append(data)
                    temps.append(data['temperature'])
            
            if cities_data:
                # Diagram
                fig = go.Figure(data=[
                    go.Bar(
                        x=[d['city'] for d in cities_data],
                        y=[d['temperature'] for d in cities_data],
                        text=[f"{d['temperature']:.1f}°C" for d in cities_data],
                        textposition='auto',
                        marker_color=['#1E88E5', '#FF7043', '#43A047', '#AB47BC', '#FFCA28']
                    )
                ])
                
                fig.update_layout(
                    title='Városok hőmérséklet összehasonlítása',
                    yaxis_title='Hőmérséklet (°C)',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Táblázatos összehasonlítás
                st.subheader("📋 Összehasonlító táblázat")
                
                comparison_df = pd.DataFrame(cities_data)
                st.dataframe(
                    comparison_df[['city', 'temperature', 'humidity', 'description']],
                    use_container_width=True
                )
    
    def run(self):
        """Alkalmazás futtatása"""
        # Oldalsáv
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/1163/1163661.png", width=100)
            st.title("Időjárás Dashboard")
            
            page = st.radio(
                "Navigáció:",
                ["🏠 Aktuális", "📈 Előzmények", "📊 Statisztikák", "🏙️ Összehasonlítás"]
            )
            
            st.divider()
            
            # API állapot
            if st.button("🏓 API ellenőrzés"):
                try:
                    response = requests.get(f"{API_URL}/", timeout=3)
                    if response.status_code == 200:
                        st.success("✅ API elérhető")
                    else:
                        st.error("❌ API nem elérhető")
                except:
                    st.error("❌ API nem elérhető")
            
            st.caption(f"Backend: {API_URL}")
            st.caption(f"Frissítve: {datetime.now().strftime('%H:%M:%S')}")
        
        # Fő tartalom
        if page == "🏠 Aktuális":
            self.display_current_weather()
        elif page == "📈 Előzmények":
            self.display_history()
        elif page == "📊 Statisztikák":
            self.display_stats()
        elif page == "🏙️ Összehasonlítás":
            self.display_comparison()

# Alkalmazás futtatása
if __name__ == "__main__":
    app = WeatherApp()
    app.run()