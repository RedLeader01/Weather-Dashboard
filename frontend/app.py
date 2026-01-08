"""
🌤️ Weather Dashboard Frontend - Fő alkalmazás
"""
import streamlit as st
from datetime import datetime
import webbrowser
import sys
import os

# Fontos: Python path beállítása a megfelelő importokhoz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import saját modulok
from config import config
from api_client import WeatherAPIClient
from components.sidebar import display_sidebar

# Manuálisan importáljuk az egyes oldalakat a views mappából
from views import (
    current as current_page,
    history as history_page, 
    stats as stats_page,
    comparison as comparison_page,
    forecast as forecast_page,
    settings as settings_page
)

# ============================================
# 1. ALKALMAZÁS INICIALIZÁLÁSA
# ============================================

# Oldal konfiguráció
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.APP_LAYOUT,
    initial_sidebar_state="expanded"
)

# CSS stílusok betöltése
def load_css():
    """CSS stílusok betöltése"""
    css_paths = [
        "frontend/styles/style.css",
        "styles/style.css",
        os.path.join(os.path.dirname(__file__), "styles", "style.css")
    ]
    
    for css_path in css_paths:
        if os.path.exists(css_path):
            try:
                with open(css_path, "r", encoding="utf-8") as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                return True
            except:
                continue
    
    # Ha nem találja a fájlt, használjuk a beágyazott CSS-t
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
            color: white !important;
            margin: 10px 0;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .forecast-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            color: #333333 !important;
            transition: all 0.3s ease;
        }
        .metric-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            border-left: 5px solid #1E88E5;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            color: #333333 !important;
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
        .quick-forecast-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
            border-radius: 10px !important;
            padding: 15px !important;
            text-align: center !important;
            color: #333333 !important;
            border: 1px solid #e0e0e0;
        }
        .weather-icon-container {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            padding: 8px;
            display: inline-block;
            margin: 8px 0;
            backdrop-filter: blur(5px);
        }
    </style>
    """, unsafe_allow_html=True)
    
    return False

# CSS betöltése
load_css()

# Session state inicializálása
def init_session_state():
    """Session state inicializálása"""
    default_values = {
        'page': 'current',
        'api_url': config.BACKEND_URL,
        'last_refresh': datetime.now(),
        'selected_cities': config.DEFAULT_CITIES[:3],
        'forecast_cache': {}
    }
    
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================
# 2. OLDAL ROUTING - SAJÁT IMPLEMENTÁCIÓ
# ============================================

def display_page(api_client):
    """Oldal kiválasztása és megjelenítése - SAJÁT NAVIGÁCIÓ"""
    page = st.session_state.page
    
    # Oldal mapping
    if page == 'current':
        current_page.display(api_client, config.DEFAULT_CITIES)
    elif page == 'history':
        history_page.display(api_client, config.DEFAULT_CITIES)
    elif page == 'stats':
        stats_page.display(api_client, config.DEFAULT_CITIES)
    elif page == 'comparison':
        comparison_page.display(api_client, config.DEFAULT_CITIES)
    elif page == 'forecast':
        forecast_page.display(api_client, config.DEFAULT_CITIES)
    elif page == 'settings':
        settings_page.display(api_client, config.DEFAULT_CITIES)
    else:
        # Alapértelmezett
        current_page.display(api_client, config.DEFAULT_CITIES)

# ============================================
# 3. FŐ ALKALMAZÁS
# ============================================

def main():
    """Fő alkalmazás"""
    
    # Inicializálás
    init_session_state()
    
    # API kliens létrehozása
    api_client = WeatherAPIClient(st.session_state.api_url)
    
    # Oldalsáv megjelenítése
    display_sidebar(api_client, config)
    
    # Oldal renderelése
    display_page(api_client)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption("🌤️ Weather Dashboard v2.2 | Eszterházy Károly Katolikus Egyetem | Multi-paradigmás programozás")
    
    with col2:
        if st.button("📚 API Dokumentáció", key="api_docs"):
            webbrowser.open(f"{api_client.base_url}/docs")
    
    with col3:
        if st.button("🔄 Oldal frissítése", key="refresh_page"):
            st.rerun()

# ============================================
# 4. ALKALMAZÁS INDÍTÁSA
# ============================================

if __name__ == "__main__":
    main()