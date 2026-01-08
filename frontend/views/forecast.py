"""7 napos előrejelzés oldal"""
import streamlit as st
import pandas as pd
from datetime import datetime

def display(api_client, cities):
    """7 napos időjárás előrejelzés megjelenítése"""
    st.markdown('<h1 class="main-header">🌤️ 7 Napos Időjárás Előrejelzés</h1>', unsafe_allow_html=True)
    
    # Város választó
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        city = st.selectbox(
            "Válassz várost:",
            cities,
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
            data = api_client.get_weather_forecast(city, days)
            if data:
                st.session_state.forecast_cache[cache_key] = data
            else:
                data = None
        else:
            data = st.session_state.forecast_cache[cache_key]
    
    if data and data.get('forecasts'):
        from ..utils import get_weekday, format_date
        from ..components.weather_cards import get_forecast_card_html
        from ..components.charts import create_forecast_trend_chart
        
        forecasts = data['forecasts']
        actual_days = len(forecasts)
        
        # Összefoglaló kártyák
        st.subheader(f"📅 {actual_days} napos előrejelzés - {data['city']}")
        
        # Napok megjelenítése kártyákban
        if actual_days <= 3:
            cols = st.columns(actual_days)
            for idx, forecast in enumerate(forecasts):
                with cols[idx]:
                    html_content = get_forecast_card_html(forecast, idx == 0)
                    st.markdown(html_content, unsafe_allow_html=True)
        elif actual_days <= 6:
            first_row = actual_days // 2 + actual_days % 2
            second_row = actual_days // 2
            
            # Első sor
            cols1 = st.columns(first_row)
            for idx in range(first_row):
                with cols1[idx]:
                    html_content = get_forecast_card_html(forecasts[idx], idx == 0)
                    st.markdown(html_content, unsafe_allow_html=True)
            
            # Második sor
            if second_row > 0:
                cols2 = st.columns(second_row)
                for idx in range(first_row, actual_days):
                    with cols2[idx - first_row]:
                        html_content = get_forecast_card_html(forecasts[idx], False)
                        st.markdown(html_content, unsafe_allow_html=True)
        else:
            # Három sorban jelenítjük meg (max 7 nap)
            rows = [3, 2, 2]
            
            start_idx = 0
            for row_count in rows:
                if start_idx >= actual_days:
                    break
                    
                cols = st.columns(min(row_count, actual_days - start_idx))
                for col_idx in range(min(row_count, actual_days - start_idx)):
                    idx = start_idx + col_idx
                    with cols[col_idx]:
                        html_content = get_forecast_card_html(forecasts[idx], idx == 0)
                        st.markdown(html_content, unsafe_allow_html=True)
                
                start_idx += row_count
                if start_idx < actual_days:
                    st.write("")  # Üres sor sorok között
        
        st.divider()
        
        # Részletes diagramok
        if actual_days >= 3:
            st.subheader("📈 Hőmérséklet trend")
            fig = create_forecast_trend_chart(forecasts)
            st.plotly_chart(fig, use_container_width=True)
        
        # Részletes táblázat
        st.subheader("📋 Részletes előrejelzés")
        
        forecast_data = []
        for forecast in forecasts:
            forecast_data.append({
                '📅 Nap': get_weekday(forecast['date']),
                '📆 Dátum': format_date(forecast['date']),
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
            hide_index=True
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