"""7 napos előrejelzés oldal - Teljesen Streamlit komponensekkel"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils import get_weekday, format_date, get_weather_icon 
from components.charts import create_forecast_trend_chart
from components.forecast_cards import create_forecast_card, create_compact_forecast_card

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
            cache_keys = [k for k in st.session_state.keys() 
                         if k.startswith(f"forecast_{city}")]
            for key in cache_keys:
                st.session_state.pop(key, None)
            st.rerun()
    
    # Adatok lekérése cache-el
    cache_key = f"forecast_{city}_{days}"
    
    if cache_key not in st.session_state:
        with st.spinner(f"{days} napos előrejelzés betöltése..."):
            data = api_client.get_weather_forecast(city, days)
            if data:
                st.session_state[cache_key] = data
            else:
                st.error("❌ Nem sikerült betölteni az előrejelzést")
                return
    else:
        data = st.session_state[cache_key]
    
    if data and data.get('forecasts'):

        
        forecasts = data['forecasts']
        actual_days = len(forecasts)
        city_name = data.get('city', city)
        
        # Összefoglaló kártyák
        st.subheader(f"📅 {actual_days} napos előrejelzés - {city_name}")
        
        # Választó a nézet típusához
        view_type = st.radio(
            "Nézet típusa:",
            ["Részletes kártyák", "Kompakt nézet", "Táblázat"],
            horizontal=True,
            key="forecast_view_type"
        )
        
        # Nézet kiválasztása
        if view_type == "Részletes kártyák":
            # Részletes kártyák
            for idx, forecast in enumerate(forecasts):
                is_today = (idx == 0)
                create_forecast_card(forecast, is_today)
                
        elif view_type == "Kompakt nézet":
            # Kompakt kártyák grid-ben
            if actual_days <= 3:
                cols = st.columns(actual_days)
                for idx, forecast in enumerate(forecasts):
                    with cols[idx]:
                        create_compact_forecast_card(forecast, idx == 0)
            elif actual_days <= 6:
                # Két sorban
                first_row = actual_days // 2 + actual_days % 2
                cols1 = st.columns(first_row)
                for idx in range(first_row):
                    with cols1[idx]:
                        create_compact_forecast_card(forecasts[idx], idx == 0)
                
                if actual_days > first_row:
                    cols2 = st.columns(actual_days - first_row)
                    for idx in range(first_row, actual_days):
                        with cols2[idx - first_row]:
                            create_compact_forecast_card(forecasts[idx], False)
            else:
                # Három sorban (7 nap)
                rows = [3, 2, 2]
                start_idx = 0
                for row_count in rows:
                    if start_idx >= actual_days:
                        break
                    cols = st.columns(row_count)
                    for col_idx in range(min(row_count, actual_days - start_idx)):
                        idx = start_idx + col_idx
                        with cols[col_idx]:
                            create_compact_forecast_card(forecasts[idx], idx == 0)
                    start_idx += row_count
        else:
            # Táblázatos nézet
            forecast_data = []
            for forecast in forecasts:
                # Nappali ikon használata a táblázatban is
                icon_code = forecast.get('icon', '')
                if icon_code.endswith('n'):
                    icon_code = icon_code[:-1] + 'd'
                
                forecast_data.append({
                    '📅 Nap': get_weekday(forecast['date']),
                    '📆 Dátum': format_date(forecast['date']),
                    '🌡️ Nappali': f"{forecast['day_temp']:.1f}°C",
                    '🌙 Éjszakai': f"{forecast['night_temp']:.1f}°C",
                    '📈 Max': f"{forecast['max_temp']:.1f}°C",
                    '📉 Min': f"{forecast['min_temp']:.1f}°C",
                    '💧 Pára': f"{forecast['humidity']}%",
                    '🌧️ Csapadék': f"{forecast.get('pop', 0):.1f}%",
                    '💨 Szél': f"{forecast['wind_speed']:.1f} m/s",
                    '🎯 Nyomás': f"{forecast['pressure']} hPa",
                    '☁️ Időjárás': forecast['description'].capitalize()
                })
            
            df = pd.DataFrame(forecast_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        
        st.divider()
        
        # Diagram
        if actual_days >= 3:
            st.subheader("📈 Hőmérséklet trend diagram")
            fig = create_forecast_trend_chart(forecasts)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        # Exportálás
        st.markdown("---")
        col_exp1, col_exp2 = st.columns([3, 1])
        
        with col_exp2:
            if st.button("💾 Exportálás CSV-ként", use_container_width=True):
                forecast_data = []
                for forecast in forecasts:
                    forecast_data.append({
                        'Dátum': forecast['date'],
                        'Nap': get_weekday(forecast['date']),
                        'Nappali_hőmérséklet': forecast['day_temp'],
                        'Éjszakai_hőmérséklet': forecast['night_temp'],
                        'Maximum': forecast['max_temp'],
                        'Minimum': forecast['min_temp'],
                        'Páratartalom': forecast['humidity'],
                        'Csapadék_valószínűség': forecast.get('pop', 0),
                        'Szélsebesség': forecast['wind_speed'],
                        'Légnyomás': forecast['pressure'],
                        'Leírás': forecast['description']
                    })
                
                df = pd.DataFrame(forecast_data)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSV letöltése",
                    data=csv,
                    file_name=f"elorejelzes_{city}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    else:
        st.error("❌ Nem sikerült betölteni az előrejelzést")
        st.info("Próbáld újra vagy válassz másik várost.")