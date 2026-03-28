"""
Core initialization file.
"""

from .game_engine import (
    GameEngine, Player, Grid, Position, Direction, 
    MovementProtocol, MovementEngine, GameStatistics
)
from .constants import *

__all__ = [
    'GameEngine', 'Player', 'Grid', 'Position', 'Direction',
    'MovementProtocol', 'MovementEngine', 'GameStatistics',
    'COLORS', 'PLAYER_COLORS', 'GRADE_CONFIGS', 'CHARACTER_NAMES'
]