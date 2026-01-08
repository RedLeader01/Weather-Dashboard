"""
Views package - SAJÁT NAVIGÁCIÓHOZ
"""
from .current import display as display_current
from .history import display as display_history
from .stats import display as display_stats
from .comparison import display as display_comparison
from .forecast import display as display_forecast
from .settings import display as display_settings

__all__ = [
    'display_current',
    'display_history', 
    'display_stats',
    'display_comparison',
    'display_forecast',
    'display_settings'
]