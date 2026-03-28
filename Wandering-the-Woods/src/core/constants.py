"""
Core constants and configuration for the Wandering in the Woods game.
"""

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Colors (R, G, B)
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GREEN': (34, 139, 34),      # Forest Green
    'BROWN': (139, 69, 19),      # Saddle Brown
    'LIGHT_GREEN': (144, 238, 144),  # Light Green
    'DARK_GREEN': (0, 100, 0),   # Dark Green
    'BLUE': (0, 0, 255),
    'RED': (255, 0, 0),
    'YELLOW': (255, 255, 0),
    'PURPLE': (128, 0, 128),
    'ORANGE': (255, 165, 0),
    'PINK': (255, 192, 203),
    'CYAN': (0, 255, 255),
    'GRAY': (128, 128, 128),
    'LIGHT_GRAY': (211, 211, 211),
    'DARK_GRAY': (169, 169, 169)
}

# Player colors for different characters
PLAYER_COLORS = [
    COLORS['RED'],
    COLORS['BLUE'], 
    COLORS['YELLOW'],
    COLORS['PURPLE']
]

# Grid settings
MIN_GRID_SIZE = 3
MAX_GRID_SIZE = 15
DEFAULT_GRID_SIZE = 5

# Cell size for rendering
CELL_SIZE = 40
CELL_MARGIN = 2

# UI Settings
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 150
FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 18

# Audio settings
MASTER_VOLUME = 0.7
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.8

# Game settings
DEFAULT_ANIMATION_SPEED = 500  # milliseconds between moves
FAST_ANIMATION_SPEED = 200
SLOW_ANIMATION_SPEED = 1000

# Grade level configurations
GRADE_CONFIGS = {
    'K2': {
        'grid_shape': 'square_only',
        'min_players': 2,
        'max_players': 2,
        'grid_sizes': [3, 4, 5],
        'movement_protocols': ['random'],
        'features': ['basic_stats', 'audio_prompts', 'celebrations']
    },
    '3-5': {
        'grid_shape': 'rectangular',
        'min_players': 2,
        'max_players': 4,
        'grid_sizes': list(range(3, 11)),
        'movement_protocols': ['random'],
        'features': ['multi_game_stats', 'custom_placement', 'group_movement']
    },
    '6-8': {
        'grid_shape': 'rectangular',
        'min_players': 2,
        'max_players': 4,
        'grid_sizes': list(range(3, 16)),
        'movement_protocols': ['random', 'biased_north', 'spiral', 'systematic'],
        'features': ['experiments', 'data_analysis', 'graphs', 'protocol_comparison']
    }
}

# Statistics display
STATS_DISPLAY_DURATION = 5000  # milliseconds

# Character names for different grades
CHARACTER_NAMES = {
    'K2': ['Bunny', 'Bear'],
    '3-5': ['Alex', 'Bailey', 'Casey', 'Drew'],
    '6-8': ['Explorer 1', 'Explorer 2', 'Explorer 3', 'Explorer 4']
}