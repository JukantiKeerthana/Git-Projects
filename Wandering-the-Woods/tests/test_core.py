"""
Basic tests for the Wandering in the Woods game core functionality.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.core import GameEngine, Player, Grid, Position, MovementProtocol
import pygame


def test_grid_creation():
    """Test basic grid functionality."""
    grid = Grid(5, 5)
    assert grid.width == 5
    assert grid.height == 5
    
    # Test position validation
    assert grid.is_valid_position(Position(0, 0))
    assert grid.is_valid_position(Position(4, 4))
    assert not grid.is_valid_position(Position(-1, 0))
    assert not grid.is_valid_position(Position(5, 0))
    assert not grid.is_valid_position(Position(0, 5))
    
    # Test corner positions
    corners = grid.get_corner_positions()
    assert len(corners) == 4
    assert Position(0, 0) in corners
    assert Position(4, 4) in corners
    
    print("✓ Grid creation tests passed")


def test_player_creation():
    """Test player functionality."""
    pos = Position(2, 3)
    player = Player(0, "Test Player", (255, 0, 0), pos)
    
    assert player.id == 0
    assert player.name == "Test Player"
    assert player.position.x == 2
    assert player.position.y == 3
    assert player.move_count == 0
    assert not player.is_found
    
    # Test movement
    new_pos = Position(3, 3)
    player.move(new_pos)
    assert player.position.x == 3
    assert player.position.y == 3
    assert player.move_count == 1
    
    print("✓ Player creation tests passed")


def test_game_engine_basic():
    """Test basic game engine functionality."""
    grid = Grid(3, 3)
    players = [
        Player(0, "Player 1", (255, 0, 0), Position(0, 0)),
        Player(1, "Player 2", (0, 0, 255), Position(2, 2))
    ]
    
    engine = GameEngine(grid, players, MovementProtocol.RANDOM)
    
    assert not engine.game_active
    assert len(engine.players) == 2
    
    # Start game
    engine.start_game()
    assert engine.game_active
    assert engine.current_run == 1
    
    # Run a few steps
    for _ in range(10):
        if not engine.step():
            break
    
    print("✓ Game engine basic tests passed")


def test_collision_detection():
    """Test player collision detection."""
    grid = Grid(3, 3)
    
    # Place players at same position
    players = [
        Player(0, "Player 1", (255, 0, 0), Position(1, 1)),
        Player(1, "Player 2", (0, 0, 255), Position(1, 1))
    ]
    
    engine = GameEngine(grid, players, MovementProtocol.RANDOM)
    engine.start_game()
    
    # Run one step to check collision detection
    engine.step()
    
    # Both players should be marked as found
    assert players[0].is_found
    assert players[1].is_found
    
    print("✓ Collision detection tests passed")


def test_movement_protocols():
    """Test different movement protocols."""
    grid = Grid(5, 5)
    player = Player(0, "Test", (255, 0, 0), Position(2, 2))
    
    from src.core.game_engine import MovementEngine
    
    # Test random movement
    new_pos = MovementEngine.get_next_move(player, grid, MovementProtocol.RANDOM)
    assert grid.is_valid_position(new_pos)
    
    # Test biased north movement  
    new_pos = MovementEngine.get_next_move(player, grid, MovementProtocol.BIASED_NORTH)
    assert grid.is_valid_position(new_pos)
    
    print("✓ Movement protocol tests passed")


def test_statistics():
    """Test statistics collection."""
    grid = Grid(3, 3)
    players = [
        Player(0, "Player 1", (255, 0, 0), Position(0, 0)),
        Player(1, "Player 2", (0, 0, 255), Position(2, 2))
    ]
    
    engine = GameEngine(grid, players, MovementProtocol.RANDOM)
    
    # Run a complete game
    engine.start_game()
    max_steps = 100
    step_count = 0
    
    while engine.game_active and step_count < max_steps:
        engine.step()
        step_count += 1
    
    # Check that statistics were recorded
    stats = engine.get_summary_statistics()
    if stats:  # If game completed
        assert 'total_runs' in stats
        assert stats['total_runs'] == 1
        assert 'average_moves' in stats
        
    print("✓ Statistics tests passed")


def run_all_tests():
    """Run all tests."""
    print("Running Wandering in the Woods Core Tests...")
    print("=" * 50)
    
    try:
        test_grid_creation()
        test_player_creation()
        test_game_engine_basic()
        test_collision_detection()
        test_movement_protocols()
        test_statistics()
        
        print("=" * 50)
        print("✅ All core tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Initialize pygame for tests that might need it
    pygame.init()
    
    success = run_all_tests()
    
    pygame.quit()
    
    sys.exit(0 if success else 1)