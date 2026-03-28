"""
K-2 Grade Level Implementation
Simple version for grades K-2 with square grids, 2 players, and basic features.
"""

import pygame
import random
import time
from typing import List, Tuple, Optional

from src.core.game_engine import GameEngine, Player, Grid, Position, MovementProtocol
from src.core.constants import COLORS, PLAYER_COLORS, CHARACTER_NAMES, CELL_SIZE, CELL_MARGIN


class K2GameRenderer:
    """Handles rendering for the K-2 version with simple graphics."""
    
    def __init__(self, screen: pygame.Surface, grid: Grid):
        self.screen = screen
        self.grid = grid
        self.cell_size = CELL_SIZE
        self.margin = CELL_MARGIN
        
        # Calculate grid position to center it
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        self.grid_x = (screen.get_width() - grid_width) // 2
        self.grid_y = (screen.get_height() - grid_height) // 2 - 50
        
        # Load fonts
        pygame.font.init()
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
    
    def draw_grid(self):
        """Draw the forest grid background."""
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_x = self.grid_x + x * self.cell_size
                cell_y = self.grid_y + y * self.cell_size
                
                # Alternate between light and dark green for forest effect
                if (x + y) % 2 == 0:
                    color = COLORS['LIGHT_GREEN']
                else:
                    color = COLORS['GREEN']
                
                pygame.draw.rect(self.screen, color, 
                               (cell_x, cell_y, self.cell_size, self.cell_size))
                
                # Draw border
                pygame.draw.rect(self.screen, COLORS['DARK_GREEN'], 
                               (cell_x, cell_y, self.cell_size, self.cell_size), 1)
    
    def draw_player(self, player: Player, animate: bool = True):
        """Draw a player as a simple cartoon character."""
        cell_x = self.grid_x + player.position.x * self.cell_size
        cell_y = self.grid_y + player.position.y * self.cell_size
        
        center_x = cell_x + self.cell_size // 2
        center_y = cell_y + self.cell_size // 2
        
        # Draw simple character based on player ID
        if player.id == 0:  # Bunny
            self._draw_bunny(center_x, center_y, COLORS['RED'])
        else:  # Bear
            self._draw_bear(center_x, center_y, COLORS['BLUE'])
    
    def _draw_bunny(self, x: int, y: int, color: Tuple[int, int, int]):
        """Draw a simple bunny character."""
        # Body (circle)
        pygame.draw.circle(self.screen, color, (x, y), 12)
        # Ears (small circles)
        pygame.draw.circle(self.screen, color, (x - 6, y - 10), 4)
        pygame.draw.circle(self.screen, color, (x + 6, y - 10), 4)
        # Eyes (small white dots)
        pygame.draw.circle(self.screen, COLORS['WHITE'], (x - 3, y - 2), 2)
        pygame.draw.circle(self.screen, COLORS['WHITE'], (x + 3, y - 2), 2)
        # Eye pupils
        pygame.draw.circle(self.screen, COLORS['BLACK'], (x - 3, y - 2), 1)
        pygame.draw.circle(self.screen, COLORS['BLACK'], (x + 3, y - 2), 1)
    
    def _draw_bear(self, x: int, y: int, color: Tuple[int, int, int]):
        """Draw a simple bear character."""
        # Body (circle)
        pygame.draw.circle(self.screen, color, (x, y), 12)
        # Ears (small circles)
        pygame.draw.circle(self.screen, color, (x - 8, y - 8), 3)
        pygame.draw.circle(self.screen, color, (x + 8, y - 8), 3)
        # Eyes (small white dots)
        pygame.draw.circle(self.screen, COLORS['WHITE'], (x - 4, y - 2), 2)
        pygame.draw.circle(self.screen, COLORS['WHITE'], (x + 4, y - 2), 2)
        # Eye pupils
        pygame.draw.circle(self.screen, COLORS['BLACK'], (x - 4, y - 2), 1)
        pygame.draw.circle(self.screen, COLORS['BLACK'], (x + 4, y - 2), 1)
        # Nose
        pygame.draw.circle(self.screen, COLORS['BLACK'], (x, y + 2), 1)
    
    def draw_move_counters(self, players: List[Player]):
        """Draw move counters for each player."""
        y_start = self.grid_y + self.grid.height * self.cell_size + 20
        
        for i, player in enumerate(players):
            text = self.medium_font.render(
                f"{player.name}: {player.move_count} moves", 
                True, COLORS['BLACK']
            )
            x_pos = 50 + i * 300
            self.screen.blit(text, (x_pos, y_start))
    
    def draw_celebration(self, players: List[Player]):
        """Draw celebration screen when players meet."""
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(128)
        overlay.fill(COLORS['YELLOW'])
        self.screen.blit(overlay, (0, 0))
        
        # Celebration text
        text = self.large_font.render("Hooray! You found each other!", True, COLORS['RED'])
        text_rect = text.get_rect(center=(self.screen.get_width()//2, 200))
        self.screen.blit(text, text_rect)
        
        # Show final statistics
        total_moves = sum(player.move_count for player in players)
        stats_text = self.medium_font.render(
            f"Total moves: {total_moves}", True, COLORS['BLACK']
        )
        stats_rect = stats_text.get_rect(center=(self.screen.get_width()//2, 250))
        self.screen.blit(stats_text, stats_rect)
        
        # Draw sparkles or stars around the text
        for _ in range(20):
            x = random.randint(100, self.screen.get_width() - 100)
            y = random.randint(100, 300)
            pygame.draw.circle(self.screen, COLORS['WHITE'], (x, y), 3)
    
    def draw_instructions(self):
        """Draw simple instructions for K-2 students."""
        instruction_text = "Help Bunny and Bear find each other in the forest!"
        text = self.medium_font.render(instruction_text, True, COLORS['BLACK'])
        text_rect = text.get_rect(center=(self.screen.get_width()//2, 30))
        self.screen.blit(text, text_rect)


class K2Game:
    """Main game class for K-2 grade level."""
    
    def __init__(self, screen: pygame.Surface, grid_size: int = 5):
        self.screen = screen
        self.grid_size = grid_size
        
        # Create square grid
        self.grid = Grid(grid_size, grid_size)
        
        # Create two players starting at opposite corners
        corner_positions = self.grid.get_corner_positions()
        self.players = [
            Player(0, CHARACTER_NAMES['K2'][0], COLORS['RED'], corner_positions[0]),
            Player(1, CHARACTER_NAMES['K2'][1], COLORS['BLUE'], corner_positions[3])
        ]
        
        # Create game engine
        self.engine = GameEngine(self.grid, self.players, MovementProtocol.RANDOM)
        
        # Create renderer
        self.renderer = K2GameRenderer(screen, self.grid)
        
        # Game state
        self.game_running = False
        self.celebrating = False
        self.celebration_start_time = 0
        self.auto_play = True
        self.move_timer = 0
        self.move_interval = 800  # milliseconds between moves
        
        # UI elements
        self.buttons = self._create_buttons()
        
    def _create_buttons(self) -> List[pygame.Rect]:
        """Create UI buttons."""
        button_width = 120
        button_height = 40
        
        start_button = pygame.Rect(50, 50, button_width, button_height)
        reset_button = pygame.Rect(180, 50, button_width, button_height)
        
        return [start_button, reset_button]
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was handled."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check button clicks
            if self.buttons[0].collidepoint(mouse_pos):  # Start button
                self.start_game()
                return True
            elif self.buttons[1].collidepoint(mouse_pos):  # Reset button
                self.reset_game()
                return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not self.game_running and not self.celebrating:
                    self.start_game()
                return True
            elif event.key == pygame.K_r:
                self.reset_game()
                return True
        
        return False
    
    def start_game(self):
        """Start a new game."""
        if not self.celebrating:
            self.engine.start_game()
            self.game_running = True
            self.celebrating = False
    
    def reset_game(self):
        """Reset the game to initial state."""
        # Reset players to opposite corners
        corner_positions = self.grid.get_corner_positions()
        self.players[0].reset(corner_positions[0])
        self.players[1].reset(corner_positions[3])
        
        self.engine.reset_for_new_game([corner_positions[0], corner_positions[3]])
        self.game_running = False
        self.celebrating = False
    
    def update(self, dt: int):
        """Update game state. dt is delta time in milliseconds."""
        if self.celebrating:
            # Handle celebration timeout
            if time.time() - self.celebration_start_time > 5.0:  # 5 seconds
                self.celebrating = False
                self.reset_game()
            return
        
        if self.game_running and self.auto_play:
            self.move_timer += dt
            
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                
                # Execute one game step
                continue_game = self.engine.step()
                
                if not continue_game:
                    # Game ended - all players found each other
                    self.game_running = False
                    self.celebrating = True
                    self.celebration_start_time = time.time()
    
    def draw(self):
        """Draw the entire game."""
        # Clear screen with light blue sky
        self.screen.fill(COLORS['CYAN'])
        
        # Draw instructions
        self.renderer.draw_instructions()
        
        # Draw grid
        self.renderer.draw_grid()
        
        # Draw players
        for player in self.players:
            self.renderer.draw_player(player)
        
        # Draw move counters
        self.renderer.draw_move_counters(self.players)
        
        # Draw buttons
        self._draw_buttons()
        
        # Draw celebration if active
        if self.celebrating:
            self.renderer.draw_celebration(self.players)
        
        # Draw game status
        self._draw_status()
    
    def _draw_buttons(self):
        """Draw UI buttons."""
        # Start button
        color = COLORS['GREEN'] if not self.game_running else COLORS['GRAY']
        pygame.draw.rect(self.screen, color, self.buttons[0])
        pygame.draw.rect(self.screen, COLORS['BLACK'], self.buttons[0], 2)
        
        start_text = self.renderer.small_font.render("START", True, COLORS['BLACK'])
        start_rect = start_text.get_rect(center=self.buttons[0].center)
        self.screen.blit(start_text, start_rect)
        
        # Reset button
        pygame.draw.rect(self.screen, COLORS['ORANGE'], self.buttons[1])
        pygame.draw.rect(self.screen, COLORS['BLACK'], self.buttons[1], 2)
        
        reset_text = self.renderer.small_font.render("RESET", True, COLORS['BLACK'])
        reset_rect = reset_text.get_rect(center=self.buttons[1].center)
        self.screen.blit(reset_text, reset_rect)
    
    def _draw_status(self):
        """Draw game status information."""
        if self.game_running:
            status = "Characters are wandering..."
        elif self.celebrating:
            status = "Celebration!"
        else:
            status = "Press START or SPACE to begin"
        
        text = self.renderer.medium_font.render(status, True, COLORS['BLACK'])
        text_rect = text.get_rect(center=(self.screen.get_width()//2, 
                                         self.screen.get_height() - 50))
        self.screen.blit(text, text_rect)
    
    def get_statistics(self) -> dict:
        """Get current game statistics."""
        return self.engine.get_summary_statistics()