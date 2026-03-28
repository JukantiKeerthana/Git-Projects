"""
Core game engine for the Wandering in the Woods simulation.
This module contains the fundamental classes and logic shared across all grade levels.
"""

import random
import time
from enum import Enum
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


class Direction(Enum):
    """Possible movement directions."""
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)


class MovementProtocol(Enum):
    """Different movement protocols for experimentation."""
    RANDOM = "random"
    BIASED_NORTH = "biased_north"
    SPIRAL = "spiral"
    SYSTEMATIC = "systematic"


@dataclass
class Position:
    """Represents a position on the grid."""
    x: int
    y: int
    
    def __eq__(self, other):
        return isinstance(other, Position) and self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))


class Player:
    """Represents a player/character in the woods."""
    
    def __init__(self, player_id: int, name: str, color: str, position: Position):
        self.id = player_id
        self.name = name
        self.color = color
        self.position = position
        self.move_count = 0
        self.is_found = False
        self.found_with = []  # List of player IDs found together
        
    def move(self, new_position: Position):
        """Move the player to a new position."""
        self.position = new_position
        self.move_count += 1
    
    def reset(self, new_position: Position):
        """Reset player state for a new game."""
        self.position = new_position
        self.move_count = 0
        self.is_found = False
        self.found_with = []


class Grid:
    """Represents the game grid/woods."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
    def is_valid_position(self, position: Position) -> bool:
        """Check if a position is within the grid bounds."""
        return 0 <= position.x < self.width and 0 <= position.y < self.height
    
    def get_adjacent_positions(self, position: Position) -> List[Position]:
        """Get all valid adjacent positions."""
        adjacent = []
        for direction in Direction:
            dx, dy = direction.value
            new_pos = Position(position.x + dx, position.y + dy)
            if self.is_valid_position(new_pos):
                adjacent.append(new_pos)
        return adjacent
    
    def get_random_position(self) -> Position:
        """Get a random valid position on the grid."""
        return Position(
            random.randint(0, self.width - 1),
            random.randint(0, self.height - 1)
        )
    
    def get_corner_positions(self) -> List[Position]:
        """Get the four corner positions of the grid."""
        return [
            Position(0, 0),  # Top-left
            Position(self.width - 1, 0),  # Top-right
            Position(0, self.height - 1),  # Bottom-left
            Position(self.width - 1, self.height - 1)  # Bottom-right
        ]


class MovementEngine:
    """Handles different movement protocols."""
    
    @staticmethod
    def get_next_move(player: Player, grid: Grid, protocol: MovementProtocol, 
                     other_players: List[Player] = None) -> Position:
        """Calculate the next move based on the movement protocol."""
        
        if protocol == MovementProtocol.RANDOM:
            return MovementEngine._random_move(player, grid)
        elif protocol == MovementProtocol.BIASED_NORTH:
            return MovementEngine._biased_north_move(player, grid)
        elif protocol == MovementProtocol.SPIRAL:
            return MovementEngine._spiral_move(player, grid)
        elif protocol == MovementProtocol.SYSTEMATIC:
            return MovementEngine._systematic_move(player, grid)
        else:
            return MovementEngine._random_move(player, grid)
    
    @staticmethod
    def _random_move(player: Player, grid: Grid) -> Position:
        """Random movement in any valid direction."""
        valid_moves = grid.get_adjacent_positions(player.position)
        if not valid_moves:
            return player.position
        return random.choice(valid_moves)
    
    @staticmethod
    def _biased_north_move(player: Player, grid: Grid) -> Position:
        """Movement biased towards north, but with some randomness."""
        valid_moves = grid.get_adjacent_positions(player.position)
        if not valid_moves:
            return player.position
        
        # Prefer north if possible (70% chance)
        north_pos = Position(player.position.x, player.position.y - 1)
        if north_pos in valid_moves and random.random() < 0.7:
            return north_pos
        
        return random.choice(valid_moves)
    
    @staticmethod
    def _spiral_move(player: Player, grid: Grid) -> Position:
        """Spiral movement pattern."""
        # Simplified spiral - alternates between right and down movements
        if player.move_count % 4 < 2:
            # Try to move right
            right_pos = Position(player.position.x + 1, player.position.y)
            if grid.is_valid_position(right_pos):
                return right_pos
        else:
            # Try to move down
            down_pos = Position(player.position.x, player.position.y + 1)
            if grid.is_valid_position(down_pos):
                return down_pos
        
        # Fallback to random move
        return MovementEngine._random_move(player, grid)
    
    @staticmethod
    def _systematic_move(player: Player, grid: Grid) -> Position:
        """Systematic grid coverage movement."""
        # Simple systematic approach: move right until edge, then down and left
        current_row = player.position.y
        current_col = player.position.x
        
        if current_row % 2 == 0:  # Even rows: move right
            if current_col < grid.width - 1:
                return Position(current_col + 1, current_row)
            else:
                return Position(current_col, current_row + 1)
        else:  # Odd rows: move left
            if current_col > 0:
                return Position(current_col - 1, current_row)
            else:
                return Position(current_col, current_row + 1)


@dataclass
class GameStatistics:
    """Stores statistics for a single game run."""
    run_number: int
    total_moves: int
    duration_seconds: float
    grid_size: Tuple[int, int]
    num_players: int
    movement_protocol: MovementProtocol
    player_moves: Dict[int, int]  # player_id -> move_count


class GameEngine:
    """Main game engine that orchestrates the simulation."""
    
    def __init__(self, grid: Grid, players: List[Player], 
                 movement_protocol: MovementProtocol = MovementProtocol.RANDOM):
        self.grid = grid
        self.players = players
        self.movement_protocol = movement_protocol
        self.game_statistics: List[GameStatistics] = []
        self.current_run = 0
        self.game_active = False
        self.start_time = 0
        
    def start_game(self):
        """Start a new game run."""
        self.game_active = True
        self.current_run += 1
        self.start_time = time.time()
        
        # Reset all players
        for player in self.players:
            player.is_found = False
            player.found_with = []
    
    def step(self) -> bool:
        """Execute one step of the simulation. Returns True if game continues."""
        if not self.game_active:
            return False
        
        # Move all unfound players
        unfound_players = [p for p in self.players if not p.is_found]
        
        # Group movement: if players are found together, they move as a group
        groups = self._get_player_groups(unfound_players)
        
        for group in groups:
            # All players in a group move to the same new position
            if group:
                new_position = MovementEngine.get_next_move(
                    group[0], self.grid, self.movement_protocol, self.players
                )
                for player in group:
                    player.move(new_position)
        
        # Check for collisions (players meeting)
        self._check_collisions()
        
        # Check if all players have been found
        all_found = all(player.is_found for player in self.players)
        if all_found:
            self._end_game()
            return False
        
        return True
    
    def _get_player_groups(self, unfound_players: List[Player]) -> List[List[Player]]:
        """Group players that are at the same position."""
        position_groups = {}
        
        for player in unfound_players:
            pos_key = (player.position.x, player.position.y)
            if pos_key not in position_groups:
                position_groups[pos_key] = []
            position_groups[pos_key].append(player)
        
        return list(position_groups.values())
    
    def _check_collisions(self):
        """Check for players meeting and update found status."""
        position_groups = {}
        
        for player in self.players:
            if not player.is_found:
                pos_key = (player.position.x, player.position.y)
                if pos_key not in position_groups:
                    position_groups[pos_key] = []
                position_groups[pos_key].append(player)
        
        # Mark players as found if they're in groups of 2 or more
        for position, group in position_groups.items():
            if len(group) >= 2:
                # If any player in the group was already found, mark all as found
                if any(p.is_found for p in group):
                    for player in group:
                        player.is_found = True
                        # Update found_with list
                        other_ids = [p.id for p in group if p.id != player.id]
                        player.found_with.extend(other_ids)
                        player.found_with = list(set(player.found_with))  # Remove duplicates
                elif len(group) >= 2:
                    # New meeting
                    for player in group:
                        player.is_found = True
                        other_ids = [p.id for p in group if p.id != player.id]
                        player.found_with.extend(other_ids)
    
    def _end_game(self):
        """End the current game and record statistics."""
        self.game_active = False
        end_time = time.time()
        
        total_moves = sum(player.move_count for player in self.players)
        duration = end_time - self.start_time
        player_moves = {player.id: player.move_count for player in self.players}
        
        stats = GameStatistics(
            run_number=self.current_run,
            total_moves=total_moves,
            duration_seconds=duration,
            grid_size=(self.grid.width, self.grid.height),
            num_players=len(self.players),
            movement_protocol=self.movement_protocol,
            player_moves=player_moves
        )
        
        self.game_statistics.append(stats)
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics across all runs."""
        if not self.game_statistics:
            return {}
        
        move_counts = [stat.total_moves for stat in self.game_statistics]
        durations = [stat.duration_seconds for stat in self.game_statistics]
        
        return {
            'total_runs': len(self.game_statistics),
            'average_moves': sum(move_counts) / len(move_counts),
            'shortest_run': min(move_counts),
            'longest_run': max(move_counts),
            'average_duration': sum(durations) / len(durations),
            'shortest_duration': min(durations),
            'longest_duration': max(durations)
        }
    
    def reset_for_new_game(self, new_positions: List[Position] = None):
        """Reset the game for a new run."""
        self.game_active = False
        
        if new_positions:
            for i, player in enumerate(self.players):
                if i < len(new_positions):
                    player.reset(new_positions[i])
        else:
            # Reset to original positions
            for player in self.players:
                player.reset(player.position)