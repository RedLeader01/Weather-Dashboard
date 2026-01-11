"""Oldalsáv komponens"""
import streamlit as st
import time
from datetime import datetime

def display_sidebar(api_client, config):
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
                response = api_client.refresh_data()
                if response:
                    st.success("✅ Adatok frissítve!")
                    st.session_state.last_refresh = datetime.now()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Frissítés sikertelen")
        
        with col2:
            if st.button("🗑️ Cache", use_container_width=True, help="Cache törlése"):
                # Töröljük a cache-t
                keys_to_delete = []
                for key in st.session_state.keys():
                    if key.startswith('current_') or key.startswith('forecast_') or key.startswith('quick_forecast_') or key.startswith('history_') or key.startswith('stats_') or key.startswith('comparison_'):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    st.session_state.pop(key, None)
                
                st.success("✅ Cache törölve")
                time.sleep(1)
                st.rerun()
        
        st.divider()
        
        # Információk
        if 'last_refresh' in st.session_state:
            st.caption(f"**Frissítve:** {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        # Város információk
        if st.button("🏙️ Városok", use_container_width=True, type="secondary"):
            cities = api_client.get_all_cities()
            if cities:
                st.info(f"**{len(cities)} város** az adatbázisban")
            else:
                st.error("❌ Nem lehet lekérdezni a városokat")