"""Diagramok és grafikonok"""
import pandas as pd
import plotly.graph_objects as go

# Közvetlen import
from utils import get_weekday

def create_temperature_chart(data: list, chart_type: str = "Vonal"):
    """Hőmérséklet diagram létrehozása"""
    if not data:
        return None
        
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
            marker=dict(size=10, color=df['humidity'], colorscale='Viridis', showscale=True),
            hovertemplate='<b>%{x|%H:%M}</b><br>Hőmérséklet: %{y:.1f}°C<br>Páratartalom: %{marker.color}%<extra></extra>'
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
    
    # Második tengely a páratartalomhoz
    if 'humidity' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['humidity'],
            mode='lines',
            name='Páratartalom',
            yaxis='y2',
            line=dict(color='#45B7D1', width=2, dash='dash'),
            hovertemplate='<b>%{x|%H:%M}</b><br>Páratartalom: %{y}%<extra></extra>'
        ))
    
    # Layout
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
        ) if 'humidity' in df.columns else {},
        height=500,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_forecast_trend_chart(forecasts: list):
    """Előrejelzés trend diagram"""
    if not forecasts:
        return None
    
    dates = [get_weekday(f['date']) for f in forecasts]
    day_temps = [f['day_temp'] for f in forecasts]
    night_temps = [f['night_temp'] for f in forecasts]
    
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