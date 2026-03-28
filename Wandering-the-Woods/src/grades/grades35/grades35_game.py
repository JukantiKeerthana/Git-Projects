"""
Grades 3-5 Implementation
Enhanced version with configurable grids, multiple players, and advanced statistics.
"""

import pygame
import random
import time
from typing import List, Tuple, Optional, Dict

from src.core.game_engine import GameEngine, Player, Grid, Position, MovementProtocol
from src.core.constants import COLORS, PLAYER_COLORS, CHARACTER_NAMES, CELL_SIZE, CELL_MARGIN


class GridConfigDialog:
    """Dialog for configuring grid settings."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        
        # Configuration state
        self.width = 5
        self.height = 5
        self.num_players = 2
        self.custom_placement = False
        
        # UI elements
        self.buttons = self._create_buttons()
        self.completed = False
        self.cancelled = False
    
    def _create_buttons(self) -> Dict[str, pygame.Rect]:
        """Create UI buttons for the configuration dialog."""
        buttons = {}
        
        # Width controls
        buttons['width_minus'] = pygame.Rect(300, 200, 40, 30)
        buttons['width_plus'] = pygame.Rect(400, 200, 40, 30)
        
        # Height controls
        buttons['height_minus'] = pygame.Rect(300, 250, 40, 30)
        buttons['height_plus'] = pygame.Rect(400, 250, 40, 30)
        
        # Player count controls
        buttons['players_minus'] = pygame.Rect(300, 300, 40, 30)
        buttons['players_plus'] = pygame.Rect(400, 300, 40, 30)
        
        # Placement toggle
        buttons['placement_toggle'] = pygame.Rect(250, 350, 200, 40)
        
        # Action buttons
        buttons['start'] = pygame.Rect(200, 450, 100, 50)
        buttons['cancel'] = pygame.Rect(350, 450, 100, 50)
        
        return buttons
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for the configuration dialog."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Width controls
            if self.buttons['width_minus'].collidepoint(mouse_pos) and self.width > 3:
                self.width -= 1
                return True
            elif self.buttons['width_plus'].collidepoint(mouse_pos) and self.width < 15:
                self.width += 1
                return True
            
            # Height controls
            elif self.buttons['height_minus'].collidepoint(mouse_pos) and self.height > 3:
                self.height -= 1
                return True
            elif self.buttons['height_plus'].collidepoint(mouse_pos) and self.height < 15:
                self.height += 1
                return True
            
            # Player count controls
            elif self.buttons['players_minus'].collidepoint(mouse_pos) and self.num_players > 2:
                self.num_players -= 1
                return True
            elif self.buttons['players_plus'].collidepoint(mouse_pos) and self.num_players < 4:
                self.num_players += 1
                return True
            
            # Placement toggle
            elif self.buttons['placement_toggle'].collidepoint(mouse_pos):
                self.custom_placement = not self.custom_placement
                return True
            
            # Action buttons
            elif self.buttons['start'].collidepoint(mouse_pos):
                self.completed = True
                return True
            elif self.buttons['cancel'].collidepoint(mouse_pos):
                self.cancelled = True
                return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.completed = True
                return True
            elif event.key == pygame.K_ESCAPE:
                self.cancelled = True
                return True
        
        return False
    
    def draw(self):
        """Draw the configuration dialog."""
        # Semi-transparent background
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(200)
        overlay.fill(COLORS['BLACK'])
        self.screen.blit(overlay, (0, 0))
        
        # Dialog background
        dialog_rect = pygame.Rect(150, 150, 500, 400)
        pygame.draw.rect(self.screen, COLORS['WHITE'], dialog_rect)
        pygame.draw.rect(self.screen, COLORS['BLACK'], dialog_rect, 3)
        
        # Title
        title = self.font_large.render("Configure Your Grid", True, COLORS['BLACK'])
        title_rect = title.get_rect(center=(400, 180))
        self.screen.blit(title, title_rect)
        
        # Width setting
        self._draw_setting("Width:", str(self.width), 200, 'width')
        
        # Height setting
        self._draw_setting("Height:", str(self.height), 250, 'height')
        
        # Players setting
        self._draw_setting("Players:", str(self.num_players), 300, 'players')
        
        # Placement setting
        placement_text = "Custom" if self.custom_placement else "Random"
        text = self.font_medium.render(f"Placement: {placement_text}", True, COLORS['BLACK'])
        self.screen.blit(text, (170, 355))
        
        # Draw buttons
        self._draw_buttons()
    
    def _draw_setting(self, label: str, value: str, y: int, control_type: str):
        """Draw a setting with +/- controls."""
        # Label
        text = self.font_medium.render(label, True, COLORS['BLACK'])
        self.screen.blit(text, (170, y))
        
        # Minus button
        minus_button = self.buttons[f'{control_type}_minus']
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], minus_button)
        pygame.draw.rect(self.screen, COLORS['BLACK'], minus_button, 2)
        minus_text = self.font_medium.render("-", True, COLORS['BLACK'])
        minus_rect = minus_text.get_rect(center=minus_button.center)
        self.screen.blit(minus_text, minus_rect)
        
        # Value
        value_text = self.font_medium.render(value, True, COLORS['BLACK'])
        value_rect = value_text.get_rect(center=(370, y + 15))
        self.screen.blit(value_text, value_rect)
        
        # Plus button
        plus_button = self.buttons[f'{control_type}_plus']
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], plus_button)
        pygame.draw.rect(self.screen, COLORS['BLACK'], plus_button, 2)
        plus_text = self.font_medium.render("+", True, COLORS['BLACK'])
        plus_rect = plus_text.get_rect(center=plus_button.center)
        self.screen.blit(plus_text, plus_rect)
    
    def _draw_buttons(self):
        """Draw action buttons."""
        # Placement toggle button
        toggle_button = self.buttons['placement_toggle']
        color = COLORS['GREEN'] if self.custom_placement else COLORS['GRAY']
        pygame.draw.rect(self.screen, color, toggle_button)
        pygame.draw.rect(self.screen, COLORS['BLACK'], toggle_button, 2)
        
        # Start button
        start_button = self.buttons['start']
        pygame.draw.rect(self.screen, COLORS['GREEN'], start_button)
        pygame.draw.rect(self.screen, COLORS['BLACK'], start_button, 2)
        start_text = self.font_medium.render("START", True, COLORS['BLACK'])
        start_rect = start_text.get_rect(center=start_button.center)
        self.screen.blit(start_text, start_rect)
        
        # Cancel button
        cancel_button = self.buttons['cancel']
        pygame.draw.rect(self.screen, COLORS['RED'], cancel_button)
        pygame.draw.rect(self.screen, COLORS['BLACK'], cancel_button, 2)
        cancel_text = self.font_medium.render("CANCEL", True, COLORS['BLACK'])
        cancel_rect = cancel_text.get_rect(center=cancel_button.center)
        self.screen.blit(cancel_text, cancel_rect)


class PlayerPlacementMode:
    """Handles custom player placement on the grid."""
    
    def __init__(self, screen: pygame.Surface, grid: Grid, num_players: int):
        self.screen = screen
        self.grid = grid
        self.num_players = num_players
        self.placed_positions = []
        self.current_player = 0
        self.font_medium = pygame.font.Font(None, 24)
        
        # Calculate grid rendering parameters
        self.cell_size = CELL_SIZE
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        self.grid_x = (screen.get_width() - grid_width) // 2
        self.grid_y = (screen.get_height() - grid_height) // 2
        
        self.completed = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle placement events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            grid_pos = self._mouse_to_grid_position(mouse_pos)
            
            if grid_pos and grid_pos not in self.placed_positions:
                self.placed_positions.append(grid_pos)
                self.current_player += 1
                
                if self.current_player >= self.num_players:
                    self.completed = True
                
                return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and self.placed_positions:
                # Remove last placement
                self.placed_positions.pop()
                self.current_player = len(self.placed_positions)
                return True
            elif event.key == pygame.K_ESCAPE:
                # Cancel placement - use random positions
                self._place_randomly()
                self.completed = True
                return True
        
        return False
    
    def _mouse_to_grid_position(self, mouse_pos: Tuple[int, int]) -> Optional[Position]:
        """Convert mouse position to grid position."""
        x, y = mouse_pos
        
        # Check if click is within grid bounds
        if (x >= self.grid_x and x < self.grid_x + self.grid.width * self.cell_size and
            y >= self.grid_y and y < self.grid_y + self.grid.height * self.cell_size):
            
            grid_x = (x - self.grid_x) // self.cell_size
            grid_y = (y - self.grid_y) // self.cell_size
            
            return Position(grid_x, grid_y)
        
        return None
    
    def _place_randomly(self):
        """Place remaining players randomly."""
        while len(self.placed_positions) < self.num_players:
            pos = self.grid.get_random_position()
            if pos not in self.placed_positions:
                self.placed_positions.append(pos)
    
    def draw(self):
        """Draw the placement interface."""
        # Clear screen
        self.screen.fill(COLORS['LIGHT_GREEN'])
        
        # Instructions
        if self.current_player < self.num_players:
            player_name = CHARACTER_NAMES['3-5'][self.current_player]
            instruction = f"Click to place {player_name} (Player {self.current_player + 1})"
        else:
            instruction = "All players placed!"
        
        text = self.font_medium.render(instruction, True, COLORS['BLACK'])
        text_rect = text.get_rect(center=(self.screen.get_width()//2, 50))
        self.screen.blit(text, text_rect)
        
        # Draw grid
        self._draw_grid()
        
        # Draw placed players
        for i, pos in enumerate(self.placed_positions):
            self._draw_player_at_position(pos, i)
        
        # Draw help text
        help_texts = [
            "Click on grid cells to place players",
            "Backspace to undo last placement",
            "ESC to place remaining players randomly"
        ]
        
        for i, help_text in enumerate(help_texts):
            text = pygame.font.Font(None, 20).render(help_text, True, COLORS['BLACK'])
            self.screen.blit(text, (50, self.screen.get_height() - 100 + i * 25))
    
    def _draw_grid(self):
        """Draw the placement grid."""
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_x = self.grid_x + x * self.cell_size
                cell_y = self.grid_y + y * self.cell_size
                
                # Check if this position is already occupied
                pos = Position(x, y)
                if pos in self.placed_positions:
                    color = COLORS['YELLOW']
                else:
                    color = COLORS['WHITE'] if (x + y) % 2 == 0 else COLORS['LIGHT_GRAY']
                
                pygame.draw.rect(self.screen, color, 
                               (cell_x, cell_y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, COLORS['BLACK'], 
                               (cell_x, cell_y, self.cell_size, self.cell_size), 1)
    
    def _draw_player_at_position(self, pos: Position, player_index: int):
        """Draw a player at a specific position."""
        cell_x = self.grid_x + pos.x * self.cell_size
        cell_y = self.grid_y + pos.y * self.cell_size
        
        center_x = cell_x + self.cell_size // 2
        center_y = cell_y + self.cell_size // 2
        
        # Draw player as colored circle with number
        color = PLAYER_COLORS[player_index % len(PLAYER_COLORS)]
        pygame.draw.circle(self.screen, color, (center_x, center_y), 15)
        pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x, center_y), 15, 2)
        
        # Draw player number
        font = pygame.font.Font(None, 20)
        text = font.render(str(player_index + 1), True, COLORS['WHITE'])
        text_rect = text.get_rect(center=(center_x, center_y))
        self.screen.blit(text, text_rect)


class Grades35GameRenderer:
    """Handles rendering for the 3-5 grade version."""
    
    def __init__(self, screen: pygame.Surface, grid: Grid):
        self.screen = screen
        self.grid = grid
        self.cell_size = CELL_SIZE
        
        # Calculate grid position
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        self.grid_x = (screen.get_width() - grid_width) // 2
        self.grid_y = (screen.get_height() - grid_height) // 2 - 50
        
        # Fonts
        pygame.font.init()
        self.large_font = pygame.font.Font(None, 36)
        self.medium_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def draw_grid(self):
        """Draw the game grid."""
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_x = self.grid_x + x * self.cell_size
                cell_y = self.grid_y + y * self.cell_size
                
                # Alternate colors for visual appeal
                if (x + y) % 2 == 0:
                    color = COLORS['LIGHT_GREEN']
                else:
                    color = COLORS['GREEN']
                
                pygame.draw.rect(self.screen, color, 
                               (cell_x, cell_y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, COLORS['DARK_GREEN'], 
                               (cell_x, cell_y, self.cell_size, self.cell_size), 1)
    
    def draw_players(self, players: List[Player]):
        """Draw all players on the grid."""
        for player in players:
            self._draw_player(player)
    
    def _draw_player(self, player: Player):
        """Draw a single player."""
        cell_x = self.grid_x + player.position.x * self.cell_size
        cell_y = self.grid_y + player.position.y * self.cell_size
        
        center_x = cell_x + self.cell_size // 2
        center_y = cell_y + self.cell_size // 2
        
        # Player color
        color = PLAYER_COLORS[player.id % len(PLAYER_COLORS)]
        
        # Draw player as circle
        radius = 12
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x, center_y), radius, 2)
        
        # Draw player ID
        text = self.small_font.render(str(player.id + 1), True, COLORS['WHITE'])
        text_rect = text.get_rect(center=(center_x, center_y))
        self.screen.blit(text, text_rect)
        
        # Draw "found" indicator if applicable
        if player.is_found:
            pygame.draw.circle(self.screen, COLORS['YELLOW'], (center_x, center_y), radius + 3, 3)
    
    def draw_statistics_panel(self, engine: GameEngine):
        """Draw the statistics panel."""
        panel_x = 20
        panel_y = 20
        panel_width = 300
        panel_height = 200
        
        # Panel background
        pygame.draw.rect(self.screen, COLORS['WHITE'], 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, COLORS['BLACK'], 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title
        title = self.medium_font.render("Game Statistics", True, COLORS['BLACK'])
        self.screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Current game stats
        if engine.game_active:
            current_moves = sum(p.move_count for p in engine.players)
            text = self.small_font.render(f"Current Moves: {current_moves}", True, COLORS['BLACK'])
            self.screen.blit(text, (panel_x + 10, panel_y + 40))
        
        # Summary statistics
        stats = engine.get_summary_statistics()
        if stats:
            y_offset = 70
            stat_items = [
                f"Total Games: {stats['total_runs']}",
                f"Average Moves: {stats['average_moves']:.1f}",
                f"Shortest Run: {stats['shortest_run']}",
                f"Longest Run: {stats['longest_run']}"
            ]
            
            for item in stat_items:
                text = self.small_font.render(item, True, COLORS['BLACK'])
                self.screen.blit(text, (panel_x + 10, panel_y + y_offset))
                y_offset += 20


class Grades35Game:
    """Main game class for grades 3-5."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        
        # Game state
        self.state = "config"  # config, placement, playing, finished
        self.config_dialog = GridConfigDialog(screen)
        self.placement_mode = None
        self.grid = None
        self.players = []
        self.engine = None
        self.renderer = None
        
        # Game timing
        self.auto_play = True
        self.move_timer = 0
        self.move_interval = 600  # milliseconds between moves
        
        # UI elements
        self.buttons = {}
        self._create_ui_buttons()
    
    def _create_ui_buttons(self):
        """Create UI buttons for the game."""
        self.buttons = {
            'new_game': pygame.Rect(350, 20, 100, 40),
            'reset': pygame.Rect(460, 20, 80, 40),
            'play_pause': pygame.Rect(550, 20, 80, 40),
            'back': pygame.Rect(20, self.screen.get_height() - 60, 80, 40)
        }
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events based on current state."""
        if self.state == "config":
            self.config_dialog.handle_event(event)
            
            if self.config_dialog.completed:
                self._start_game_setup()
                return True
            elif self.config_dialog.cancelled:
                return False  # Return to main menu
        
        elif self.state == "placement":
            if self.placement_mode:
                self.placement_mode.handle_event(event)
                
                if self.placement_mode.completed:
                    self._finalize_game_setup()
                    return True
        
        elif self.state == "playing" or self.state == "finished":
            return self._handle_game_events(event)
        
        return True
    
    def _handle_game_events(self, event: pygame.event.Event) -> bool:
        """Handle events during gameplay."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            for button_name, button_rect in self.buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    if button_name == 'new_game':
                        self._new_game()
                    elif button_name == 'reset':
                        self._reset_current_game()
                    elif button_name == 'play_pause':
                        self._toggle_play_pause()
                    elif button_name == 'back':
                        return False  # Return to main menu
                    return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._toggle_play_pause()
            elif event.key == pygame.K_r:
                self._reset_current_game()
            elif event.key == pygame.K_n:
                self._new_game()
            return True
        
        return True
    
    def _start_game_setup(self):
        """Start setting up the game after configuration."""
        config = self.config_dialog
        
        # Create grid
        self.grid = Grid(config.width, config.height)
        
        if config.custom_placement:
            # Enter placement mode
            self.state = "placement"
            self.placement_mode = PlayerPlacementMode(self.screen, self.grid, config.num_players)
        else:
            # Use random placement
            self._create_players_random(config.num_players)
            self._finalize_game_setup()
    
    def _create_players_random(self, num_players: int):
        """Create players with random positions."""
        self.players = []
        positions = []
        
        # Generate unique random positions
        while len(positions) < num_players:
            pos = self.grid.get_random_position()
            if pos not in positions:
                positions.append(pos)
        
        # Create players
        for i in range(num_players):
            name = CHARACTER_NAMES['3-5'][i]
            color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
            player = Player(i, name, color, positions[i])
            self.players.append(player)
    
    def _finalize_game_setup(self):
        """Finalize game setup and start playing."""
        if self.placement_mode:
            # Create players from placement positions
            self.players = []
            for i, pos in enumerate(self.placement_mode.placed_positions):
                name = CHARACTER_NAMES['3-5'][i]
                color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
                player = Player(i, name, color, pos)
                self.players.append(player)
        
        # Create game engine
        self.engine = GameEngine(self.grid, self.players, MovementProtocol.RANDOM)
        
        # Create renderer
        self.renderer = Grades35GameRenderer(self.screen, self.grid)
        
        # Start the game
        self.state = "playing"
        self.engine.start_game()
    
    def _new_game(self):
        """Start a new game configuration."""
        self.state = "config"
        self.config_dialog = GridConfigDialog(self.screen)
        self.placement_mode = None
    
    def _reset_current_game(self):
        """Reset the current game."""
        if self.engine and self.players:
            # Reset players to their original positions
            original_positions = []
            if self.placement_mode:
                original_positions = self.placement_mode.placed_positions
            else:
                # For random games, generate new random positions
                for player in self.players:
                    original_positions.append(self.grid.get_random_position())
            
            for i, player in enumerate(self.players):
                player.reset(original_positions[i])
            
            self.engine.reset_for_new_game(original_positions)
            self.state = "playing"
            self.engine.start_game()
    
    def _toggle_play_pause(self):
        """Toggle between play and pause."""
        self.auto_play = not self.auto_play
    
    def update(self, dt: int):
        """Update the game state."""
        if self.state == "playing" and self.engine and self.auto_play:
            self.move_timer += dt
            
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                
                continue_game = self.engine.step()
                
                if not continue_game:
                    self.state = "finished"
    
    def draw(self):
        """Draw the current state."""
        if self.state == "config":
            self.screen.fill(COLORS['LIGHT_BLUE'])
            self.config_dialog.draw()
        
        elif self.state == "placement":
            self.placement_mode.draw()
        
        elif self.state == "playing" or self.state == "finished":
            self._draw_game()
    
    def _draw_game(self):
        """Draw the main game interface."""
        # Clear screen
        self.screen.fill(COLORS['LIGHT_BLUE'])
        
        # Draw grid and players
        if self.renderer:
            self.renderer.draw_grid()
            self.renderer.draw_players(self.players)
            self.renderer.draw_statistics_panel(self.engine)
        
        # Draw UI buttons
        self._draw_ui_buttons()
        
        # Draw status
        self._draw_status()
    
    def _draw_ui_buttons(self):
        """Draw UI buttons."""
        button_configs = {
            'new_game': ("NEW", COLORS['GREEN']),
            'reset': ("RESET", COLORS['ORANGE']),
            'play_pause': ("PAUSE" if self.auto_play else "PLAY", COLORS['BLUE']),
            'back': ("BACK", COLORS['RED'])
        }
        
        font = pygame.font.Font(None, 20)
        
        for button_name, (text, color) in button_configs.items():
            button_rect = self.buttons[button_name]
            
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, COLORS['BLACK'], button_rect, 2)
            
            text_surface = font.render(text, True, COLORS['BLACK'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_status(self):
        """Draw game status."""
        if self.state == "playing":
            status = "Searching..." if self.auto_play else "Paused"
        elif self.state == "finished":
            status = "All players found each other!"
        else:
            status = ""
        
        if status:
            font = pygame.font.Font(None, 24)
            text = font.render(status, True, COLORS['BLACK'])
            text_rect = text.get_rect(center=(self.screen.get_width()//2, 
                                             self.screen.get_height() - 30))
            self.screen.blit(text, text_rect)