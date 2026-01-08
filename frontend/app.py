"""
🌤️ Weather Dashboard Frontend - API URL változtatható
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import json

# Alapértelmezett konfiguráció
DEFAULT_CONFIG = {
    "api_url": "http://localhost:8000",
    "cities": ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr", "Miskolc"],
    "theme": "light"
}

class WeatherApp:
    """Időjárás alkalmazás osztály"""
    
    def __init__(self):
        self.init_session_state()
        
    def init_session_state(self):
        """Session state inicializálása"""
        if 'api_url' not in st.session_state:
            st.session_state.api_url = DEFAULT_CONFIG["api_url"]
        if 'config_visible' not in st.session_state:
            st.session_state.config_visible = False
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
    
    def fetch_data(self, endpoint, params=None):
        """API adatok lekérése"""
        try:
            url = f"{st.session_state.api_url}{endpoint}"
            
            # Timeout és error handling
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API hiba ({response.status_code}): {response.text[:100]}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Nem lehet csatlakozni az API-hoz: {st.session_state.api_url}")
            return None
        except Exception as e:
            st.error(f"Hiba történt: {str(e)}")
            return None
    
    def display_config_panel(self):
        """Konfigurációs panel megjelenítése"""
        with st.sidebar:
            st.subheader("⚙️ API Konfiguráció")
            
            # API URL beállítása
            new_api_url = st.text_input(
                "API URL:",
                value=st.session_state.api_url,
                help="A backend API címe (pl: http://localhost:8000)"
            )
            
            if new_api_url != st.session_state.api_url:
                st.session_state.api_url = new_api_url
                st.rerun()
            
            # API tesztelése
            if st.button("🔗 API kapcsolat tesztelése"):
                with st.spinner("Kapcsolat tesztelése..."):
                    try:
                        response = requests.get(f"{new_api_url}/health", timeout=3)
                        if response.status_code == 200:
                            st.success("✅ API elérhető!")
                        else:
                            st.error(f"❌ API hiba: {response.status_code}")
                    except:
                        st.error("❌ Nem lehet csatlakozni az API-hoz")
            
            # Aktuális konfiguráció
            with st.expander("📋 Aktuális beállítások"):
                config_info = self.fetch_data("/api/config")
                if config_info:
                    st.json(config_info)
                else:
                    st.info("API konfiguráció nem elérhető")
            
            st.divider()
    
    def display_current_weather(self):
        """Aktuális időjárás"""
        st.header("🌤️ Aktuális Időjárás")
        
        # Város választó
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            city = st.selectbox("Város:", DEFAULT_CONFIG["cities"], key="current_city")
        
        with col2:
            if st.button("🔄 Frissítés", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("📊 Statisztika", use_container_width=True):
                st.session_state.show_stats = True
        
        # Adatok lekérése
        data = self.fetch_data("/api/weather", {"city": city})
        
        if data:
            # Fő kártya
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Hőmérséklet és leírás
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          border-radius: 15px; padding: 30px; color: white;'>
                    <h1 style='font-size: 4rem; margin: 0;'>{data['temperature']:.1f}°C</h1>
                    <h2 style='margin-top: 10px;'>{city}</h2>
                    <p style='font-size: 1.5rem;'>{data['description'].capitalize()}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Ikon
                if data.get('icon'):
                    icon_url = f"https://openweathermap.org/img/wn/{data['icon']}@4x.png"
                    st.image(icon_url, width=150)
            
            # Metrikák
            cols = st.columns(4)
            metrics = [
                ("💧 Páratartalom", f"{data['humidity']}%"),
                ("🎯 Nyomás", f"{data.get('pressure', 'N/A')} hPa"),
                ("💨 Szél", f"{data.get('wind_speed', 'N/A')} m/s"),
                ("🕐 Frissítve", datetime.fromisoformat(
                    data['timestamp'].replace('Z', '+00:00')
                ).strftime("%H:%M"))
            ]
            
            for col, (label, value) in zip(cols, metrics):
                with col:
                    st.metric(label, value)
    
    def display_history(self):
        """Előzmények diagrammal"""
        st.header("📈 Időjárás Előzmények")
        
        col1, col2 = st.columns(2)
        with col1:
            city = st.selectbox("Város:", DEFAULT_CONFIG["cities"], key="history_city")
        with col2:
            limit = st.slider("Rekordok:", 5, 50, 20, key="history_limit")
        
        data = self.fetch_data("/api/weather/history", {"city": city, "limit": limit})
        
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
                name='Hőmérséklet',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['humidity'],
                mode='lines',
                name='Páratartalom',
                yaxis='y2',
                line=dict(color='#4ECDC4', width=2, dash='dash')
            ))
            
            fig.update_layout(
                title=f'{city} - Időjárás trend',
                xaxis_title='Idő',
                yaxis_title='Hőmérséklet (°C)',
                yaxis2=dict(
                    title='Páratartalom (%)',
                    overlaying='y',
                    side='right'
                ),
                height=500,
                template='plotly_white',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Részletes adatok
            with st.expander("📋 Részletes adatok"):
                display_df = df[['timestamp', 'temperature', 'humidity', 'description']].copy()
                display_df['timestamp'] = display_df['timestamp'].dt.strftime('%m.%d %H:%M')
                st.dataframe(display_df, use_container_width=True)
    
    def display_statistics(self):
        """Statisztikák"""
        st.header("📊 Statisztikák")
        
        col1, col2 = st.columns(2)
        with col1:
            city = st.selectbox("Város:", DEFAULT_CONFIG["cities"], key="stats_city")
        with col2:
            hours = st.selectbox(
                "Időtartam:",
                [6, 12, 24, 48, 72, 168],
                index=2,
                format_func=lambda x: f"{x} óra"
            )
        
        data = self.fetch_data("/api/weather/stats", {"city": city, "hours": hours})
        
        if data:
            # Metrikák
            cols = st.columns(4)
            metrics = [
                ("📈 Átlag", f"{data['avg_temperature']:.1f}°C"),
                ("📉 Minimum", f"{data['min_temperature']:.1f}°C"),
                ("📈 Maximum", f"{data['max_temperature']:.1f}°C"),
                ("🔢 Mérések", data['record_count'])
            ]
            
            for col, (label, value) in zip(cols, metrics):
                with col:
                    st.metric(label, value)
            
            # Infobox
            st.info(f"""
            **Statisztikai információk:**
            
            - **Város:** {data['city']}
            - **Időtartam:** utolsó {hours} óra
            - **Összes mérés:** {data['record_count']}
            - **Hőmérséklet tartomány:** {data['min_temperature']:.1f}°C - {data['max_temperature']:.1f}°C
            - **Átlag páratartalom:** {data['avg_humidity']:.1f}%
            - **Utolsó frissítés:** {data['last_update']}
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
    
    def display_comparison(self):
        """Városok összehasonlítása"""
        st.header("🏙️ Városok Összehasonlítása")
        
        selected_cities = st.multiselect(
            "Válassz városokat:",
            DEFAULT_CONFIG["cities"],
            default=DEFAULT_CONFIG["cities"][:3]
        )
        
        if len(selected_cities) < 2:
            st.warning("⚠️ Válassz legalább 2 várost az összehasonlításhoz!")
            return
        
        # Adatok gyűjtése
        cities_data = []
        for city in selected_cities:
            data = self.fetch_data("/api/weather", {"city": city})
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
                text=[f"{d['temperature']:.1f}°C" for d in cities_data],
                textposition='auto',
                marker_color='#95E1D3',
                hovertemplate='<b>%{x}</b><br>Hőmérséklet: %{y:.1f}°C<br>Páratartalom: %{customdata}%<extra></extra>',
                customdata=[d['humidity'] for d in cities_data]
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
                'Hőmérséklet (°C)': f"{data['temperature']:.1f}",
                'Páratartalom (%)': data['humidity'],
                'Leírás': data['description'].capitalize(),
                'Frissítve': datetime.fromisoformat(
                    data['timestamp'].replace('Z', '+00:00')
                ).strftime('%H:%M')
            })
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
    
    def display_sidebar(self):
        """Oldalsáv megjelenítése"""
        with st.sidebar:
            # Logo
            st.image("https://cdn-icons-png.flaticon.com/512/1163/1163661.png", width=80)
            st.title("🌤️ Időjárás")
            
            # Navigáció
            page = st.radio(
                "Navigáció:",
                ["🏠 Aktuális", "📈 Előzmények", "📊 Statisztikák", "🏙️ Összehasonlítás"],
                index=0
            )
            
            st.divider()
            
            # API konfiguráció
            self.display_config_panel()
            
            # Aktuális információk
            st.caption(f"API: {st.session_state.api_url}")
            if st.session_state.last_update:
                st.caption(f"Utolsó frissítés: {st.session_state.last_update}")
            
            # Manuális frissítés gomb
            if st.button("🔄 Összes város frissítése"):
                response = self.fetch_data("/api/refresh")
                if response:
                    st.success("✅ Frissítés elindítva!")
                    time.sleep(1)
                    st.rerun()
    
    def run(self):
        """Alkalmazás futtatása"""
        # Oldalsáv
        self.display_sidebar()
        
        # Fő tartalom
        page = st.session_state.get('page', "🏠 Aktuális")
        
        if page == "🏠 Aktuális":
            self.display_current_weather()
        elif page == "📈 Előzmények":
            self.display_history()
        elif page == "📊 Statisztikák":
            self.display_statistics()
        elif page == "🏙️ Összehasonlítása":
            self.display_comparison()
        
        # Footer
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.caption("🌤️ Weather Dashboard v2.0")
        with col2:
            if st.button("ℹ️ API Info"):
                st.session_state.show_api_info = True
        with col3:
            if st.button("🔄 Oldal frissítése"):
                st.rerun()
        
        # API info modal
        if st.session_state.get('show_api_info'):
            with st.expander("API Információk", expanded=True):
                endpoints = [
                    ("GET /", "Főoldal"),
                    ("GET /health", "Health check"),
                    ("GET /api/weather?city={city}", "Aktuális időjárás"),
                    ("GET /api/weather/history?city={city}&limit={n}", "Előzmények"),
                    ("GET /api/weather/stats?city={city}&hours={h}", "Statisztikák"),
                    ("GET /api/cities", "Városok listája"),
                    ("POST /api/refresh", "Manuális frissítés")
                ]
                
                for endpoint, desc in endpoints:
                    st.code(f"{st.session_state.api_url}{endpoint}", language=None)
                    st.caption(desc)
                    st.write("")

# Alkalmazás indítása
if __name__ == "__main__":
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
        margin-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Alkalmazás futtatása
    app = WeatherApp()
    app.run()