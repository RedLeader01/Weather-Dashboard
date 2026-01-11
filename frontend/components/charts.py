"""Diagramok és grafikonok - Javított változat Streamlit Cloud-hoz"""
import pandas as pd
import plotly.graph_objects as go
from utils import get_weekday

def create_temperature_chart(data: list, chart_type: str = "Vonal"):
    """Hőmérséklet diagram létrehozása - Hibakezeléssel"""
    if not data or len(data) == 0:
        # Üres diagram visszaadása
        fig = go.Figure()
        fig.update_layout(
            title='Nincs adat a diagramhoz',
            height=400,
            template='plotly_white'
        )
        return fig
        
    try:
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        df['time_formatted'] = df['timestamp'].dt.strftime('%m.%d %H:%M')
        
        fig = go.Figure()
        
        if chart_type == "Vonal":
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                mode='lines+markers',
                name='Hőmérséklet',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8, color='#FF6B6B'),
                hovertemplate='<b>%{x|%H:%M}</b><br>Hőmérséklet: %{y:.1f}°C<extra></extra>'
            ))
        elif chart_type == "Oszlop":
            fig.add_trace(go.Bar(
                x=df['time_formatted'],
                y=df['temperature'],
                name='Hőmérséklet',
                marker_color='#4ECDC4',
                hovertemplate='<b>%{x}</b><br>Hőmérséklet: %{y:.1f}°C<extra></extra>'
            ))
        elif chart_type == "Pont":
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                mode='markers',
                name='Hőmérséklet',
                marker=dict(size=10, color=df['humidity'] if 'humidity' in df.columns else df['temperature'], 
                           colorscale='Viridis', showscale=True),
                hovertemplate='<b>%{x|%H:%M}</b><br>Hőmérséklet: %{y:.1f}°C<extra></extra>'
            ))
        else:  # Terület
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                mode='lines',
                name='Hőmérséklet',
                fill='tozeroy',
                fillcolor='rgba(255, 107, 107, 0.2)',
                line=dict(color='#FF6B6B', width=2),
                hovertemplate='<b>%{x|%H:%M}</b><br>Hőmérséklet: %{y:.1f}°C<extra></extra>'
            ))
        
        # Második tengely a páratartalomhoz - CSAK HA VAN ADAT
        if 'humidity' in df.columns and len(df['humidity'].dropna()) > 0:
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['humidity'],
                mode='lines',
                name='Páratartalom',
                yaxis='y2',
                line=dict(color='#45B7D1', width=2, dash='dash'),
                hovertemplate='<b>%{x|%H:%M}</b><br>Páratartalom: %{y}%<extra></extra>'
            ))
            
            # Layout második tengellyel
            fig.update_layout(
                xaxis_title='Idő',
                yaxis_title='Hőmérséklet (°C)',
                yaxis=dict(titlefont=dict(color='#FF6B6B'), tickfont=dict(color='#FF6B6B')),
                yaxis2=dict(
                    title='Páratartalom (%)',
                    titlefont=dict(color='#45B7D1'),
                    tickfont=dict(color='#45B7D1'),
                    overlaying='y',
                    side='right'
                ),
                height=500,
                template='plotly_white',
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
        else:
            # Layout második tengely NÉLKÜL
            fig.update_layout(
                xaxis_title='Idő',
                yaxis_title='Hőmérséklet (°C)',
                yaxis=dict(titlefont=dict(color='#FF6B6B'), tickfont=dict(color='#FF6B6B')),
                height=500,
                template='plotly_white',
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
        
        return fig
        
    except Exception as e:
        # Hibás diagram visszaadása a hibaüzenettel
        fig = go.Figure()
        fig.add_annotation(
            text=f"Hiba a diagram létrehozásánál: {str(e)[:100]}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(height=400, template='plotly_white')
        return fig

def create_forecast_trend_chart(forecasts: list):
    """Előrejelzés trend diagram - Hibakezeléssel"""
    if not forecasts or len(forecasts) == 0:
        fig = go.Figure()
        fig.update_layout(
            title='Nincs előrejelzési adat',
            height=400,
            template='plotly_white'
        )
        return fig
    
    try:
        dates = [get_weekday(f['date']) for f in forecasts]
        day_temps = [f.get('day_temp', 0) for f in forecasts]
        night_temps = [f.get('night_temp', 0) for f in forecasts]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=day_temps,
            mode='lines+markers',
            name='Nappali',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=10, color='#FF6B6B')
        ))
        fig.add_trace(go.Scatter(
            x=dates,
            y=night_temps,
            mode='lines+markers',
            name='Éjszakai',
            line=dict(color='#45B7D1', width=3, dash='dash'),
            marker=dict(size=8, color='#45B7D1')
        ))
        
        fig.update_layout(
            xaxis_title='Nap',
            yaxis_title='Hőmérséklet (°C)',
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Hiba a trend diagram létrehozásánál: {str(e)[:100]}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(height=400, template='plotly_white')
        return fig