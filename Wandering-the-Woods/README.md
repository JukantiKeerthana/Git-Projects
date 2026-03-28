# Wandering in the Woods - Educational Simulation

## 🎮 Quick Start for Users

**Simply double-click `WanderingInTheWoods` executable to run - no installation needed!**

## 📚 What is this?

An educational simulation teaching computational thinking to K-8 students through interactive forest exploration games.

## Project Structure

```
FinalProject/
├── src/                    # Source code
│   ├── core/              # Core game engine components
│   ├── grades/            # Grade-specific implementations
│   │   ├── k2/           # Grades K-2
│   │   ├── grades35/     # Grades 3-5
│   │   └── grades68/     # Grades 6-8
│   ├── ui/               # User interface components
│   ├── audio/            # Audio management
│   └── utils/            # Utility functions
├── assets/               # Game assets
│   ├── images/          # Character sprites and graphics
│   ├── sounds/          # Audio files
│   └── fonts/           # Font files
├── docs/                # Documentation
├── tests/               # Test files
├── dist/                # Distribution/executable files
├── requirements.txt     # Python dependencies
└── main.py             # Main entry point
```

## Features by Grade Level

### K-2 (Ages 5-7)
- Simple square grids
- 2 cartoon characters starting from opposite corners
- Random movement with visual counters
- Background music and celebration sounds
- Basic statistics with audio announcements

### 3-5 (Ages 8-10)
- Configurable rectangular grids
- 2-4 players with custom starting positions
- Group movement mechanics
- Multi-game statistics tracking
- Enhanced data visualization

### 6-8 (Ages 11-13)
- Experimental mode for grid analysis
- Multiple movement protocols
- Data analysis and graphing
- Big data concepts introduction
- Advanced statistical features

## Installation & Usage

See `docs/UserGuide.md` for detailed installation and usage instructions.

## Development

This project is built using Python and pygame for cross-platform compatibility and rich multimedia support.