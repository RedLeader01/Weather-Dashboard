"""
🌤️ Weather Dashboard Frontend - Fő alkalmazás
"""
import streamlit as st
import webbrowser
import sys
import os
from datetime import datetime

# Python path beállítása a megfelelő importokhoz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import saját modulok
from config import config
from api_client import WeatherAPIClient

# Oldalsáv komponens import (közvetlenül)
from components.sidebar import display_sidebar

# Oldalak importálása
import importlib.util
import os

# Dinamikus importálás az oldalaknak
def import_page(module_name, file_path):
    """Dinamikusan importál egy modult"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Importáljuk az oldalakat
current_page = import_page("current", "views/current.py")
history_page = import_page("history", "views/history.py")
stats_page = import_page("stats", "views/stats.py")
comparison_page = import_page("comparison", "views/comparison.py")
forecast_page = import_page("forecast", "views/forecast.py")
settings_page = import_page("settings", "views/settings.py")

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

# CSS betöltés
def load_css():
    """CSS stílusok betöltése"""
    css_paths = [
        os.path.join(os.path.dirname(__file__), "styles", "style.css"),
        "styles/style.css",
        "frontend/styles/style.css"
    ]
    
    for css_path in css_paths:
        if os.path.exists(css_path):
            try:
                with open(css_path, "r", encoding="utf-8") as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                return True
            except:
                continue
    
    # Backup CSS
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
        
        /* Kártya stílusok */
        .streamlit-container {
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        
        /* Ma kiemelése */
        .today-card {
            border-left: 5px solid #1E88E5 !important;
            background: linear-gradient(135deg, #f0f7ff 0%, #e3f2fd 100%) !important;
        }
        
        /* Gombok */
        .stButton>button {
            border-radius: 8px !important;
            font-weight: bold !important;
        }
        
        /* Metrikák */
        .metric-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #1E88E5;
        }
        
        /* Elrejtjük az auto-navigation-t */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Reszponzív design */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem !important;
            }
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
        'forecast_cache': {},
        'app_initialized': False
    }
    
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================
# 2. KAPCSOLAT ELLENŐRZÉS
# ============================================

def check_backend_connection(api_client):
    """Backend kapcsolat ellenőrzése"""
    try:
        health_data = api_client.get_health()
        if health_data:
            st.session_state.app_initialized = True
            return True
        else:
            st.session_state.app_initialized = False
            return False
    except:
        st.session_state.app_initialized = False
        return False

def display_welcome_screen(api_client):
    """Üdvözlő képernyő ha nincs kapcsolat"""
    st.markdown('<h1 class="main-header">🌤️ Időjárás Dashboard</h1>', unsafe_allow_html=True)
    
    st.info("""
    **Üdvözöljük az Időjárás Dashboard-ban!**
    
    Az alkalmazás betöltése folyamatban...
    """)
    
    # Kapcsolat ellenőrzése
    with st.spinner("Backend kapcsolat ellenőrzése..."):
        if check_backend_connection(api_client):
            st.success("✅ Sikeres kapcsolat a backenddel!")
            st.rerun()
            return True
        else:
            st.error("❌ Nem sikerült kapcsolódni a backendhez")
            
            st.markdown("""
            **Hibaelhárítás:**
            1. Ellenőrizd, hogy a backend fut-e: `http://localhost:8000`
            2. Indítsd el a backendet: `cd backend && uvicorn main:app --reload`
            3. Próbáld újra a kapcsolatot
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Újrapróbálkozás", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("⚙️ Beállítások", use_container_width=True):
                    st.session_state.page = 'settings'
                    st.rerun()
            
            return False

# ============================================
# 3. OLDAL ROUTING
# ============================================

def display_page(api_client):
    """Oldal kiválasztása és megjelenítése"""
    page = st.session_state.page
    
    # Ha nincs inicializálva, jelenítsük meg az üdvözlőt
    if not st.session_state.get('app_initialized', False):
        if not display_welcome_screen(api_client):
            return
    
    # Oldal routing
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
# 4. FŐ ALKALMAZÁS
# ============================================

def main():
    """Fő alkalmazás"""
    
    # Inicializálás
    init_session_state()
    
    # API kliens létrehozása
    api_client = WeatherAPIClient(st.session_state.api_url)
    
    # Oldalsáv megjelenítése
    display_sidebar(api_client, config)
    
    # Oldal tartalom
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
# 5. INDÍTÁS
# ============================================

if __name__ == "__main__":
    main()