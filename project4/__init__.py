"""
Strategies Package - Contains all trading strategies
"""

from .moving_average import MovingAverageStrategy
from .mean_reversion import MeanReversionStrategy
from .breakout import BreakoutStrategy

__all__ = [
    'MovingAverageStrategy',
    'MeanReversionStrategy',
    'BreakoutStrategy'
]