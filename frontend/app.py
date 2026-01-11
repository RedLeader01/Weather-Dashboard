"""
🌤️ Weather Dashboard Frontend - Fő alkalmazás (Streamlit Cloud kompatibilis)
"""
import streamlit as st
import webbrowser
import sys
import os
from datetime import datetime

# ============================================
# 1. PATH BEÁLLÍTÁSA STREAMLIT CLOUD SZERINT
# ============================================

# Streamlit Cloud a repository gyökeréből futtat, de a fájlok a frontend/ mappában vannak
current_dir = os.path.dirname(os.path.abspath(__file__))

# Ha a frontend mappában vagyunk (lokális fejlesztés)
if current_dir.endswith('frontend'):
    sys.path.insert(0, current_dir)
    frontend_dir = current_dir
else:
    # Ha a gyökérben vagyunk (Streamlit Cloud)
    # Próbáljuk megtalálni a frontend mappát
    frontend_dir = os.path.join(current_dir, 'frontend')
    if not os.path.exists(frontend_dir):
        # Ha nincs frontend mappa, akkor itt vagyunk benne
        frontend_dir = current_dir
    sys.path.insert(0, frontend_dir)

# Import saját modulok
try:
    from config import config
    from api_client import WeatherAPIClient
except ImportError as e:
    st.error(f"Import hiba: {e}")
    # Próbáljuk meg másképp
    try:
        sys.path.insert(0, os.path.join(frontend_dir, '..'))
        from frontend.config import config
        from frontend.api_client import WeatherAPIClient
    except:
        st.error("Nem sikerült importálni a modulokat")
        config = None
        WeatherAPIClient = None

# ============================================
# 2. OLDALAK IMPORTÁLÁSA (Streamlit Cloud kompatibilis)
# ============================================

def load_page(module_name):
    """Dinamikusan importál egy oldalt"""
    try:
        # Először próbáljuk a frontend/views/ mappából
        views_dir = os.path.join(frontend_dir, 'views')
        module_path = os.path.join(views_dir, f"{module_name}.py")
        
        if os.path.exists(module_path):
            # Dinamikus importálás fájlból
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        else:
            # Próbáljuk importálni a Python path-ról
            import importlib
            return importlib.import_module(f"views.{module_name}")
    except Exception as e:
        st.error(f"Hiba a(z) {module_name} oldal betöltésénél: {e}")
        # Visszatérünk egy dummy modullal, ami csak hibaüzenetet jelenít meg
        class DummyPage:
            @staticmethod
            def display(api_client, cities):
                st.error(f"A(z) {module_name} oldal betöltése sikertelen")
                st.info("Próbáld újratölteni az oldalt, vagy ellenőrizd a konzolt.")
        
        return DummyPage

# Importáljuk az oldalakat
try:
    current_page = load_page("current")
    history_page = load_page("history")
    stats_page = load_page("stats")
    comparison_page = load_page("comparison")
    forecast_page = load_page("forecast")
    settings_page = load_page("settings")
except Exception as e:
    st.error(f"Hiba az oldalak importálásakor: {e}")
    # Hiba esetén hozzunk létre dummy oldalakat
    class DummyPage:
        @staticmethod
        def display(api_client, cities):
            st.error("Oldal betöltési hiba")

    current_page = history_page = stats_page = comparison_page = forecast_page = settings_page = DummyPage

# ============================================
# 3. ALKALMAZÁS INICIALIZÁLÁSA
# ============================================

# Oldal konfiguráció
st.set_page_config(
    page_title=config.APP_TITLE if config else "Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stílusok betöltése
def load_css():
    """CSS stílusok betöltése"""
    css_paths = [
        os.path.join(frontend_dir, "styles", "style.css"),
        os.path.join(frontend_dir, "style.css"),
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
    
    # Backup CSS ha a fájl nem található
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
            color: white !important; 
            margin: 10px 0; 
            box-shadow: 0 10px 20px rgba(0,0,0,0.1); 
        }
        .stButton>button { 
            width: 100%; 
            border-radius: 8px; 
            font-weight: bold; 
        }
        [data-testid="stSidebarNav"] { 
            display: none !important; 
        }
    </style>
    """, unsafe_allow_html=True)
    return False

# CSS betöltése
load_css()

# Session state inicializálása
def init_session_state():
    """Session state inicializálása"""
    if config:
        default_cities = config.DEFAULT_CITIES
    else:
        default_cities = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr", "Miskolc", "Nyíregyháza"]
    
    default_values = {
        'page': 'current',
        'api_url': config.BACKEND_URL if config else "http://localhost:8000",
        'last_refresh': datetime.now(),
        'selected_cities': default_cities[:3],
        'forecast_cache': {},
        'app_initialized': False
    }
    
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================
# 4. OLDALSÁV KOMPONENS (inline, nem importáljuk)
# ============================================

def display_sidebar(api_client, config_obj):
    """Oldalsáv megjelenítése - inline implementáció"""
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
            if st.button("🗑️ Cache", use_container_width=True, help="Cache törlése"):
                # Töröljük a cache-t
                keys_to_delete = []
                for key in st.session_state.keys():
                    if key.startswith('current_') or key.startswith('forecast_') or key.startswith('quick_forecast_') or key.startswith('history_') or key.startswith('stats_') or key.startswith('comparison_'):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    st.session_state.pop(key, None)
                
                st.success("✅ Cache törölve")
                st.rerun()
        
        st.divider()
        
        # Információk
        if 'last_refresh' in st.session_state:
            st.caption(f"**Frissítve:** {st.session_state.last_refresh.strftime('%H:%M:%S')}")

# ============================================
# 5. KAPCSOLAT ELLENŐRZÉS
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
            1. Ellenőrizd, hogy a backend fut-e
            2. Próbáld újra a kapcsolatot
            """)
            
            if st.button("🔄 Újrapróbálkozás", use_container_width=True):
                st.rerun()
            
            return False

# ============================================
# 6. OLDAL ROUTING
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
        current_page.display(api_client, config.DEFAULT_CITIES if config else ["Budapest", "Debrecen", "Szeged"])
    elif page == 'history':
        history_page.display(api_client, config.DEFAULT_CITIES if config else ["Budapest", "Debrecen", "Szeged"])
    elif page == 'stats':
        stats_page.display(api_client, config.DEFAULT_CITIES if config else ["Budapest", "Debrecen", "Szeged"])
    elif page == 'comparison':
        comparison_page.display(api_client, config.DEFAULT_CITIES if config else ["Budapest", "Debrecen", "Szeged"])
    elif page == 'forecast':
        forecast_page.display(api_client, config.DEFAULT_CITIES if config else ["Budapest", "Debrecen", "Szeged"])
    elif page == 'settings':
        settings_page.display(api_client, config.DEFAULT_CITIES if config else ["Budapest", "Debrecen", "Szeged"])
    else:
        # Alapértelmezett
        current_page.display(api_client, config.DEFAULT_CITIES if config else ["Budapest", "Debrecen", "Szeged"])

# ============================================
# 7. FŐ ALKALMAZÁS
# ============================================

def main():
    """Fő alkalmazás"""
    
    # Inicializálás
    init_session_state()
    
    # API kliens létrehozása
    try:
        api_client = WeatherAPIClient(st.session_state.api_url)
    except:
        st.error("Nem sikerült létrehozni az API klienst")
        return
    
    # Oldalsáv megjelenítése (inline)
    display_sidebar(api_client, config)
    
    # Oldal tartalom
    display_page(api_client)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption("🌤️ Weather Dashboard | Eszterházy Károly Katolikus Egyetem | Multi-paradigmás programozás")
    
    with col2:
        if st.button("📚 API Dokumentáció", key="api_docs"):
            webbrowser.open(f"{api_client.base_url}/docs")
    
    with col3:
        if st.button("🔄 Oldal frissítése", key="refresh_page"):
            st.rerun()

# ============================================
# 8. INDÍTÁS
# ============================================

if __name__ == "__main__":
    main()