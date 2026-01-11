"""Időjárás előzmények oldal - Javított"""
import streamlit as st
import pandas as pd

def display(api_client, cities):
    """Időjárás előzmények megjelenítése"""
    st.markdown('<h1 class="main-header">📈 Időjárás Előzmények</h1>', unsafe_allow_html=True)
    
    # Beállítások
    col1, col2, col3 = st.columns(3)
    
    with col1:
        city = st.selectbox("Város:", cities, key="history_city")
    
    with col2:
        limit = st.slider("Rekordok száma:", 5, 50, 20, key="history_limit")
    
    with col3:
        chart_type = st.selectbox(
            "Diagram típusa:",
            ["Vonal", "Oszlop", "Pont", "Terület"],
            key="chart_type"
        )
    
    # Adatok lekérése cache-el
    cache_key = f"history_{city}_{limit}"
    
    if cache_key not in st.session_state:
        with st.spinner(f"{city} előzményeinek betöltése..."):
            try:
                data = api_client.get_weather_history(city, limit)
                if data:
                    st.session_state[cache_key] = data
                else:
                    st.session_state[cache_key] = []
            except:
                st.session_state[cache_key] = []
    else:
        data = st.session_state[cache_key]
    
    if data and len(data) > 0:
        try:
            from components.charts import create_temperature_chart
            from utils import format_time
            
            # Diagram
            fig = create_temperature_chart(data, chart_type)
            fig.update_layout(title=f'{city} - Időjárás előzmények')
            st.plotly_chart(fig, use_container_width=True)
            
            # Statisztikák
            st.subheader("📊 Statisztikai összefoglaló")
            
            df = pd.DataFrame(data)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                temp_avg = df['temperature'].mean() if 'temperature' in df.columns else 0
                st.metric("Átlag hőmérséklet", f"{temp_avg:.1f}°C")
            
            with col2:
                temp_min = df['temperature'].min() if 'temperature' in df.columns else 0
                st.metric("Minimum", f"{temp_min:.1f}°C")
            
            with col3:
                temp_max = df['temperature'].max() if 'temperature' in df.columns else 0
                st.metric("Maximum", f"{temp_max:.1f}°C")
            
            with col4:
                temp_std = df['temperature'].std() if 'temperature' in df.columns else 0
                st.metric("Változatosság", f"{temp_std:.1f}°C")
            
            # Részletes adatok
            with st.expander("📋 Részletes adatok", expanded=False):
                display_df = df.copy()
                
                # Csak létező oszlopok
                columns_to_show = []
                if 'timestamp' in display_df.columns:
                    display_df['timestamp'] = display_df['timestamp'].apply(format_time)
                    columns_to_show.append('timestamp')
                
                if 'temperature' in display_df.columns:
                    columns_to_show.append('temperature')
                
                if 'humidity' in display_df.columns:
                    columns_to_show.append('humidity')
                
                if 'pressure' in display_df.columns:
                    columns_to_show.append('pressure')
                
                if 'wind_speed' in display_df.columns:
                    columns_to_show.append('wind_speed')
                
                if 'description' in display_df.columns:
                    columns_to_show.append('description')
                
                if columns_to_show:
                    display_df = display_df[columns_to_show]
                    # Oszlopnevek átnevezése
                    column_names = {
                        'timestamp': 'Idő',
                        'temperature': 'Hőmérséklet (°C)',
                        'humidity': 'Páratartalom (%)',
                        'pressure': 'Nyomás (hPa)',
                        'wind_speed': 'Szél (m/s)',
                        'description': 'Leírás'
                    }
                    display_df.rename(columns=column_names, inplace=True)
                    st.dataframe(display_df, use_container_width=True, height=400)
                else:
                    st.info("Nincs megjeleníthető adat.")
                    
        except Exception as e:
            st.error(f"Hiba történt az adatok feldolgozásánál: {str(e)}")
            st.info("Próbáld újra vagy válassz másik várost.")
    
    else:
        st.warning(f"⚠️ Nincs elég adat {city} városhoz")
        st.info("Használd a '🔄 Frissítés' gombot az oldalsávban több adat gyűjtéséhez.")