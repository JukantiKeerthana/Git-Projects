"""
Wandering in the Woods - Educational Simulation Game
Main entry point implementing the full requirements for K-8 students.
"""

import pygame
import sys
import os
import random
import time
from typing import Optional, List, Tuple, Dict

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Try to use text-to-speech for audio announcements
TTS_AVAILABLE = False
# Disable TTS to prevent button interaction issues
TTS_AVAILABLE = False
print("🔇 Text-to-speech disabled for better button responsiveness")

class AudioManager:
    """Handles audio announcements and music."""
    
    def __init__(self):
        pygame.mixer.init()
        # Disable TTS to prevent button interaction issues
        self.tts_engine = None
        print("🔇 Audio disabled for better performance")
    
    def speak(self, text: str):
        """Speak text using TTS or print to console."""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except:
                print(f"TTS: {text}")
        else:
            print(f"🔊 {text}")
    
    def play_celebration_sound(self):
        """Play a simple celebration beep."""
        try:
            # Create a simple celebration tone
            duration = 200
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            arr = []
            for i in range(frames):
                wave = 4096 * (i % 100 < 50)  # Square wave
                arr.append([wave, wave])
            sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
            sound.play()
        except:
            pass  # No audio available

class Grid:
    """Represents the game grid."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_random_position(self) -> Tuple[int, int]:
        return (random.randint(0, self.width - 1), random.randint(0, self.height - 1))

class Player:
    """Represents a player/character in the woods."""
    
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], name: str, player_id: int):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.id = player_id
        self.moves = 0
        self.found = False
        self.group_members = []  # For 3-5 grade group movement
    
    def move_random(self, grid: Grid) -> bool:
        """Move randomly to adjacent cell. Returns True if moved."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = self.x + dx, self.y + dy
            if grid.is_valid_position(new_x, new_y):
                self.x, self.y = new_x, new_y
                self.moves += 1
                return True
        return False
    
    def move_to(self, x: int, y: int):
        """Move to specific position (for group movement)."""
        self.x, self.y = x, y
        self.moves += 1

class GameStatistics:
    """Tracks game statistics across multiple runs."""
    
    def __init__(self):
        self.runs = []
        self.current_run_start = None
    
    def start_run(self):
        self.current_run_start = time.time()
    
    def end_run(self, total_moves: int, players: List[Player]):
        if self.current_run_start:
            duration = time.time() - self.current_run_start
            self.runs.append({
                'moves': total_moves,
                'duration': duration,
                'player_moves': [p.moves for p in players]
            })
    
    def get_summary(self) -> Dict:
        if not self.runs:
            return {}
        
        moves_list = [run['moves'] for run in self.runs]
        return {
            'total_runs': len(self.runs),
            'average_moves': sum(moves_list) / len(moves_list),
            'shortest_run': min(moves_list),
            'longest_run': max(moves_list),
            'last_run_moves': moves_list[-1] if moves_list else 0
        }

class K2Game:
    """K-2 Grade Level: Simple visualization with student interaction."""
    
    def __init__(self, screen: pygame.Surface, audio: AudioManager):
        self.screen = screen
        self.audio = audio
        
        # Always 5x5 square grid for K-2
        self.grid = Grid(5, 5)
        self.cell_size = 60
        
        # Always 2 players at diagonal corners
        self.players = [
            Player(0, 0, (255, 100, 100), "🐰 Bunny", 0),
            Player(4, 4, (100, 100, 255), "🐻 Bear", 1)
        ]
        
        # Game state
        self.running = True
        self.paused = True  # Start paused so students can choose to begin
        self.game_over = False
        self.move_timer = 0
        self.move_interval = 1000  # 1 second between moves
        self.celebration_timer = 0
        self.stats = GameStatistics()
        
        # UI elements
        self.font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        
        # Buttons for student interaction
        self.start_button = pygame.Rect(350, 600, 120, 40)
        self.reset_button = pygame.Rect(480, 600, 120, 40)
        
        self.audio.speak("Welcome to the Wandering Woods! Bunny and Bear are lost. Click START to help them search for each other!")
        
    def handle_event(self, event) -> bool:
        """Handle user input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(event.pos):
                if self.paused and not self.game_over:
                    self.start_new_game()
                    return True
            elif self.reset_button.collidepoint(event.pos):
                self.reset_game()
                return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.paused and not self.game_over:
                    self.start_new_game()
                elif not self.game_over:
                    self.paused = not self.paused
                return True
            elif event.key == pygame.K_r:
                self.reset_game()
                return True
            elif event.key == pygame.K_m:
                return "menu"  # Return to main menu
            elif event.key == pygame.K_ESCAPE:
                return False
        
        return True
        
    def start_new_game(self):
        """Start a new game run."""
        # Reset positions to diagonal corners
        self.players[0].x, self.players[0].y = 0, 0
        self.players[1].x, self.players[1].y = 4, 4
        
        # Reset player state
        for player in self.players:
            player.moves = 0
            player.found = False
        
        self.paused = False
        self.game_over = False
        self.celebration_timer = 0
        self.move_timer = 0
        
        self.stats.start_run()
        self.audio.speak("The search begins! Watch Bunny and Bear wander through the forest!")
    
    def reset_game(self):
        """Reset to initial state."""
        self.players[0].x, self.players[0].y = 0, 0
        self.players[1].x, self.players[1].y = 4, 4
        
        for player in self.players:
            player.moves = 0
            player.found = False
        
        self.paused = True
        self.game_over = False
        self.celebration_timer = 0
        self.move_timer = 0
        
        self.audio.speak("Game reset! Click START when you're ready to begin a new search!")
    
    def update(self, dt: int):
        """Update game state."""
        if self.paused:
            return
            
        if self.game_over:
            self.celebration_timer += dt
            if self.celebration_timer >= 5000:  # 5 second celebration
                self.reset_game()
            return
        
        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            
            # Move unfound players
            for player in self.players:
                if not player.found:
                    player.move_random(self.grid)
            
            self.check_meetings()
    
    def check_meetings(self):
        """Check if players have met."""
        if self.players[0].x == self.players[1].x and self.players[0].y == self.players[1].y:
            if not self.game_over:
                for player in self.players:
                    player.found = True
                
                total_moves = sum(p.moves for p in self.players)
                self.stats.end_run(total_moves, self.players)
                
                self.game_over = True
                self.celebration_timer = 0
                
                self.audio.play_celebration_sound()
                self.audio.speak(f"Hooray! Bunny and Bear found each other! Bunny took {self.players[0].moves} steps and Bear took {self.players[1].moves} steps. That's {total_moves} steps total!")
    
    def draw(self):
        """Draw the K-2 game."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        LIGHT_GREEN = (144, 238, 144)
        GREEN = (100, 200, 100)
        YELLOW = (255, 255, 100)
        BLUE = (100, 150, 255)
        RED = (255, 100, 100)
        
        self.screen.fill(WHITE)
        
        # Title
        title = "Wandering in the Woods - Grades K-2"
        title_text = self.large_font.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(500, 40))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        if self.paused and not self.game_over:
            instruction = "Click START to help Bunny 🐰 and Bear 🐻 search for each other!"
        elif self.game_over:
            instruction = "Great job! Watch the celebration, then we'll start a new search!"
        else:
            instruction = "Watch them search! Each step counts!"
            
        inst_text = self.font.render(instruction, True, BLACK)
        inst_rect = inst_text.get_rect(center=(500, 80))
        self.screen.blit(inst_text, inst_rect)
        
        # Calculate grid position (centered)
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        grid_x = (1000 - grid_width) // 2
        grid_y = 150
        
        # Draw grid
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_x = grid_x + x * self.cell_size
                cell_y = grid_y + y * self.cell_size
                
                color = LIGHT_GREEN if (x + y) % 2 == 0 else GREEN
                pygame.draw.rect(self.screen, color, 
                               (cell_x, cell_y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, BLACK, 
                               (cell_x, cell_y, self.cell_size, self.cell_size), 2)
        
        # Draw players
        for player in self.players:
            cell_x = grid_x + player.x * self.cell_size
            cell_y = grid_y + player.y * self.cell_size
            center_x = cell_x + self.cell_size // 2
            center_y = cell_y + self.cell_size // 2
            
            # Draw player circle
            radius = 20
            pygame.draw.circle(self.screen, player.color, (center_x, center_y), radius)
            pygame.draw.circle(self.screen, BLACK, (center_x, center_y), radius, 3)
            
            # Draw celebration effect if found
            if player.found:
                for i in range(3):
                    pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), radius + 8 + i*3, 2)
        
        # Draw move counters
        counter_y = grid_y + grid_height + 30
        bunny_text = f"🐰 Bunny: {self.players[0].moves} steps"
        bear_text = f"🐻 Bear: {self.players[1].moves} steps"
        
        bunny_surface = self.font.render(bunny_text, True, BLACK)
        bear_surface = self.font.render(bear_text, True, BLACK)
        
        self.screen.blit(bunny_surface, (200, counter_y))
        self.screen.blit(bear_surface, (500, counter_y))
        
        # Draw statistics
        stats = self.stats.get_summary()
        if stats:
            stats_y = counter_y + 40
            stats_text = f"Games played: {stats['total_runs']} | Average steps: {stats['average_moves']:.1f} | Best: {stats['shortest_run']}"
            stats_surface = pygame.font.Font(None, 24).render(stats_text, True, BLACK)
            stats_rect = stats_surface.get_rect(center=(500, stats_y))
            self.screen.blit(stats_surface, stats_rect)
        
        # Draw buttons
        # START button
        start_color = GREEN if (self.paused and not self.game_over) else (150, 150, 150)
        pygame.draw.rect(self.screen, start_color, self.start_button)
        pygame.draw.rect(self.screen, BLACK, self.start_button, 2)
        start_text = self.font.render("START" if self.paused else "RUNNING", True, BLACK)
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_rect)
        
        # RESET button
        pygame.draw.rect(self.screen, RED, self.reset_button)
        pygame.draw.rect(self.screen, BLACK, self.reset_button, 2)
        reset_text = self.font.render("NEW GAME", True, BLACK)
        reset_rect = reset_text.get_rect(center=self.reset_button.center)
        self.screen.blit(reset_text, reset_rect)
        
        # Control instructions
        control_text = "Press SPACE to pause/resume, R to reset, M for Main Menu, ESC to exit"
        control_surface = self.small_font.render(control_text, True, BLACK)
        control_rect = control_surface.get_rect(center=(500, 550))
        self.screen.blit(control_surface, control_rect)


class Grades35Game:
    """Grades 3-5: Rectangular grids, 2-4 players, group movement when found."""
    
    def __init__(self, screen: pygame.Surface, audio: AudioManager):
        self.screen = screen
        self.audio = audio
        
        # Configuration state
        self.state = "setup"  # setup, placement, playing, game_over
        self.grid_width = 6
        self.grid_height = 4  # Rectangular grid
        self.num_players = 2
        self.cell_size = 45
        
        # Player placement
        self.placement_mode = "corners"  # corners, random, manual
        self.placing_player = 0
        self.player_positions = []
        
        # Game components
        self.grid = None
        self.players = []
        self.stats = GameStatistics()
        
        # Group movement - players that found each other move together
        self.player_groups = []  # List of player groups that move together
        
        # Game state
        self.paused = False
        self.game_over = False
        self.move_timer = 0
        self.move_interval = 600
        self.celebration_timer = 0
        
        # UI
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)
        
        self.audio.speak("Welcome to Advanced Forest Explorer! Configure your rectangular grid and place your team of 2 to 4 explorers!")
    
    def handle_event(self, event) -> bool:
        """Handle user input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "setup":
                return self.handle_setup_click(event.pos)
            elif self.state == "placement":
                return self.handle_placement_click(event.pos)
            elif self.state == "playing" or self.state == "game_over":
                return self.handle_game_click(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_m:
                return "menu"  # Return to main menu
            elif self.state == "playing":
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset_game()
        
        return True
    
    def handle_setup_click(self, pos) -> bool:
        """Handle setup configuration clicks."""
        # Grid width controls
        if pygame.Rect(200, 200, 30, 30).collidepoint(pos) and self.grid_width > 3:
            self.grid_width -= 1
        elif pygame.Rect(270, 200, 30, 30).collidepoint(pos) and self.grid_width < 15:
            self.grid_width += 1
        
        # Grid height controls  
        elif pygame.Rect(200, 250, 30, 30).collidepoint(pos) and self.grid_height > 3:
            self.grid_height -= 1
        elif pygame.Rect(270, 250, 30, 30).collidepoint(pos) and self.grid_height < 12:
            self.grid_height += 1
        
        # Player count controls
        elif pygame.Rect(200, 300, 30, 30).collidepoint(pos) and self.num_players > 2:
            self.num_players -= 1
        elif pygame.Rect(270, 300, 30, 30).collidepoint(pos) and self.num_players < 4:
            self.num_players += 1
        
        # Placement mode buttons
        elif pygame.Rect(350, 200, 150, 35).collidepoint(pos):
            self.placement_mode = "corners"
            self.start_game_corners()
        elif pygame.Rect(350, 245, 150, 35).collidepoint(pos):
            self.placement_mode = "random"
            self.start_game_random()
        elif pygame.Rect(350, 290, 150, 35).collidepoint(pos):
            self.placement_mode = "manual"
            self.start_manual_placement()
        
        return True
    
    def start_game_corners(self):
        """Start game with players at corners."""
        self.grid = Grid(self.grid_width, self.grid_height)
        
        colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 165, 0)]
        names = ["🔴 Red Explorer", "🔵 Blue Explorer", "🟢 Green Explorer", "🟠 Orange Explorer"]
        
        # Place at corners and edges
        positions = [
            (0, 0),  # Top-left
            (self.grid_width-1, self.grid_height-1),  # Bottom-right
            (0, self.grid_height-1),  # Bottom-left
            (self.grid_width-1, 0)   # Top-right
        ]
        
        self.players = []
        self.player_groups = []
        
        for i in range(self.num_players):
            x, y = positions[i]
            player = Player(x, y, colors[i], names[i], i)
            self.players.append(player)
        
        self.state = "playing"
        self.paused = False
        self.game_over = False
        self.stats.start_run()
        
        self.audio.speak(f"Game started! {self.num_players} explorers begin their search in a {self.grid_width} by {self.grid_height} forest!")
    
    def start_game_random(self):
        """Start game with random player placement.""" 
        self.grid = Grid(self.grid_width, self.grid_height)
        
        colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 165, 0)]
        names = ["🔴 Red Explorer", "🔵 Blue Explorer", "🟢 Green Explorer", "🟠 Orange Explorer"]
        
        # Get unique random positions
        positions = []
        while len(positions) < self.num_players:
            pos = self.grid.get_random_position()
            if pos not in positions:
                positions.append(pos)
        
        self.players = []
        self.player_groups = []
        
        for i in range(self.num_players):
            x, y = positions[i]
            player = Player(x, y, colors[i], names[i], i)
            self.players.append(player)
        
        self.state = "playing"
        self.paused = False
        self.game_over = False
        self.stats.start_run()
        
        self.audio.speak(f"Random placement! {self.num_players} explorers start their search!")
    
    def start_manual_placement(self):
        """Start manual player placement mode."""
        self.grid = Grid(self.grid_width, self.grid_height)
        self.state = "placement"
        self.placing_player = 0
        self.player_positions = []
        self.players = []
        
        self.audio.speak("Click on the grid to place your explorers one by one!")
    
    def handle_placement_click(self, pos) -> bool:
        """Handle clicks during manual placement."""
        # Calculate grid position
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        grid_x = (1000 - grid_width) // 2
        grid_y = 100
        
        # Check if click is within grid
        if (grid_x <= pos[0] <= grid_x + grid_width and 
            grid_y <= pos[1] <= grid_y + grid_height):
            
            # Convert to grid coordinates
            grid_pos_x = (pos[0] - grid_x) // self.cell_size
            grid_pos_y = (pos[1] - grid_y) // self.cell_size
            
            # Check if position is valid and not occupied
            if (0 <= grid_pos_x < self.grid_width and 
                0 <= grid_pos_y < self.grid_height and
                (grid_pos_x, grid_pos_y) not in self.player_positions):
                
                self.player_positions.append((grid_pos_x, grid_pos_y))
                
                # Create player
                colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 165, 0)]
                names = ["🔴 Red Explorer", "🔵 Blue Explorer", "🟢 Green Explorer", "🟠 Orange Explorer"]
                
                player = Player(grid_pos_x, grid_pos_y, colors[self.placing_player], 
                              names[self.placing_player], self.placing_player)
                self.players.append(player)
                
                self.placing_player += 1
                
                if self.placing_player >= self.num_players:
                    # All players placed, start game
                    self.state = "playing"
                    self.paused = False
                    self.game_over = False
                    self.player_groups = []
                    self.stats.start_run()
                    
                    self.audio.speak("All explorers placed! The search begins!")
                else:
                    self.audio.speak(f"Place explorer {self.placing_player + 1}")
        
        return True
    
    def handle_game_click(self, pos) -> bool:
        """Handle clicks during gameplay."""
        # Pause/Play button
        if pygame.Rect(50, 600, 80, 30).collidepoint(pos):
            self.paused = not self.paused
        # Reset button
        elif pygame.Rect(140, 600, 80, 30).collidepoint(pos):
            self.reset_game()
        # New Setup button
        elif pygame.Rect(230, 600, 100, 30).collidepoint(pos):
            self.state = "setup"
        
        return True
    
    def reset_game(self):
        """Reset the current game."""
        if hasattr(self, 'players') and self.players:
            # Reset to original positions
            colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 165, 0)]
            names = ["🔴 Red Explorer", "🔵 Blue Explorer", "🟢 Green Explorer", "🟠 Orange Explorer"]
            
            if self.placement_mode == "corners":
                positions = [(0, 0), (self.grid_width-1, self.grid_height-1), 
                           (0, self.grid_height-1), (self.grid_width-1, 0)]
            elif hasattr(self, 'player_positions'):
                positions = self.player_positions
            else:
                positions = [(0, 0), (self.grid_width-1, self.grid_height-1), 
                           (0, self.grid_height-1), (self.grid_width-1, 0)]
            
            for i, player in enumerate(self.players):
                if i < len(positions):
                    x, y = positions[i]
                    player.x, player.y = x, y
                player.moves = 0
                player.found = False
                player.group_members = []
            
            self.player_groups = []
            self.paused = False
            self.game_over = False
            self.celebration_timer = 0
            self.stats.start_run()
    
    def update(self, dt: int):
        """Update game state."""
        if self.state != "playing" or self.paused:
            return
        
        if self.game_over:
            self.celebration_timer += dt
            if self.celebration_timer >= 4000:
                self.reset_game()
            return
        
        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            self.move_players_with_groups()
            self.check_meetings()
    
    def move_players_with_groups(self):
        """Move players with group movement logic."""
        moved_players = set()
        
        # Move groups together
        for group in self.player_groups:
            if group and group[0] not in moved_players:
                # Leader decides the move
                leader = self.players[group[0]]
                old_x, old_y = leader.x, leader.y
                
                if leader.move_random(self.grid):
                    # Move all group members to the same position
                    for player_id in group[1:]:
                        if player_id < len(self.players):
                            follower = self.players[player_id]
                            follower.move_to(leader.x, leader.y)
                            moved_players.add(player_id)
                
                moved_players.add(group[0])
        
        # Move individual players not in groups
        for player in self.players:
            if player.id not in moved_players and not self.player_in_group(player.id):
                player.move_random(self.grid)
    
    def player_in_group(self, player_id: int) -> bool:
        """Check if player is in any group."""
        for group in self.player_groups:
            if player_id in group:
                return True
        return False
    
    def check_meetings(self):
        """Check for meetings and form groups."""
        # Group players by position
        position_groups = {}
        for player in self.players:
            pos = (player.x, player.y)
            if pos not in position_groups:
                position_groups[pos] = []
            position_groups[pos].append(player.id)
        
        # Check for new meetings
        for pos, player_ids in position_groups.items():
            if len(player_ids) > 1:
                # Players met - form or merge groups
                self.form_or_merge_groups(player_ids)
                
                # Mark players as found
                for pid in player_ids:
                    if pid < len(self.players):
                        self.players[pid].found = True
        
        # Check if all players are in one group (game over)
        if len(self.player_groups) == 1 and len(self.player_groups[0]) == self.num_players:
            total_moves = sum(p.moves for p in self.players)
            self.stats.end_run(total_moves, self.players)
            
            self.game_over = True
            self.celebration_timer = 0
            
            self.audio.speak(f"Victory! All {self.num_players} explorers found each other! Total moves: {total_moves}")
    
    def form_or_merge_groups(self, meeting_player_ids):
        """Form new group or merge existing groups when players meet."""
        # Find which groups these players belong to
        involved_groups = []
        ungrouped_players = []
        
        for pid in meeting_player_ids:
            found_group = False
            for i, group in enumerate(self.player_groups):
                if pid in group:
                    if i not in involved_groups:
                        involved_groups.append(i)
                    found_group = True
                    break
            
            if not found_group:
                ungrouped_players.append(pid)
        
        # Merge all involved groups and add ungrouped players
        new_group = ungrouped_players.copy()
        
        for group_index in sorted(involved_groups, reverse=True):
            new_group.extend(self.player_groups[group_index])
            del self.player_groups[group_index]
        
        # Remove duplicates and add new merged group
        new_group = list(set(new_group))
        if new_group:
            self.player_groups.append(new_group)
            
            player_names = [self.players[pid].name.split()[1] if pid < len(self.players) else f"Player{pid+1}" 
                          for pid in new_group]
            self.audio.speak(f"Explorers {', '.join(player_names)} have found each other and will now search together!")
    
    def draw(self):
        """Draw the 3-5 game."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        LIGHT_GREEN = (144, 238, 144)
        GREEN = (100, 200, 100)
        YELLOW = (255, 255, 100)
        BLUE = (100, 150, 255)
        RED = (255, 100, 100)
        GRAY = (150, 150, 150)
        
        self.screen.fill(WHITE)
        
        if self.state == "setup":
            self.draw_setup_screen()
        elif self.state == "placement":
            self.draw_placement_screen()
        else:
            self.draw_game_screen()
    
    def draw_setup_screen(self):
        """Draw setup configuration screen."""
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        GREEN = (100, 200, 100)
        GRAY = (200, 200, 200)
        LIGHT_GREEN = (144, 238, 144)
        
        # Title
        title = "Advanced Forest Explorer Configuration - Grades 3-5"
        title_text = self.large_font.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(500, 50))
        self.screen.blit(title_text, title_rect)
        
        # Configuration options
        config_text = f"Grid: {self.grid_width} × {self.grid_height} (rectangular!)"
        text = self.font.render(config_text, True, BLACK)
        self.screen.blit(text, (150, 170))
        
        # Width controls
        width_text = f"Width: {self.grid_width}"
        text = self.font.render(width_text, True, BLACK)
        self.screen.blit(text, (100, 200))
        
        # Draw +/- buttons
        minus_btn = pygame.Rect(200, 200, 30, 30)
        plus_btn = pygame.Rect(270, 200, 30, 30)
        pygame.draw.rect(self.screen, GRAY, minus_btn)
        pygame.draw.rect(self.screen, BLACK, minus_btn, 2)
        pygame.draw.rect(self.screen, GRAY, plus_btn)
        pygame.draw.rect(self.screen, BLACK, plus_btn, 2)
        
        minus_text = self.font.render("-", True, BLACK)
        plus_text = self.font.render("+", True, BLACK)
        self.screen.blit(minus_text, (minus_btn.x + 10, minus_btn.y + 5))
        self.screen.blit(plus_text, (plus_btn.x + 10, plus_btn.y + 5))
        
        # Height controls
        height_text = f"Height: {self.grid_height}"
        text = self.font.render(height_text, True, BLACK)
        self.screen.blit(text, (100, 250))
        
        minus_btn = pygame.Rect(200, 250, 30, 30)
        plus_btn = pygame.Rect(270, 250, 30, 30)
        pygame.draw.rect(self.screen, GRAY, minus_btn)
        pygame.draw.rect(self.screen, BLACK, minus_btn, 2)
        pygame.draw.rect(self.screen, GRAY, plus_btn)
        pygame.draw.rect(self.screen, BLACK, plus_btn, 2)
        
        self.screen.blit(minus_text, (minus_btn.x + 10, minus_btn.y + 5))
        self.screen.blit(plus_text, (plus_btn.x + 10, plus_btn.y + 5))
        
        # Player count controls
        players_text = f"Explorers: {self.num_players}"
        text = self.font.render(players_text, True, BLACK)
        self.screen.blit(text, (100, 300))
        
        minus_btn = pygame.Rect(200, 300, 30, 30)
        plus_btn = pygame.Rect(270, 300, 30, 30)
        pygame.draw.rect(self.screen, GRAY, minus_btn)
        pygame.draw.rect(self.screen, BLACK, minus_btn, 2)
        pygame.draw.rect(self.screen, GRAY, plus_btn)
        pygame.draw.rect(self.screen, BLACK, plus_btn, 2)
        
        self.screen.blit(minus_text, (minus_btn.x + 10, minus_btn.y + 5))
        self.screen.blit(plus_text, (plus_btn.x + 10, plus_btn.y + 5))
        
        # Placement buttons
        corner_btn = pygame.Rect(350, 200, 150, 35)
        random_btn = pygame.Rect(350, 245, 150, 35) 
        manual_btn = pygame.Rect(350, 290, 150, 35)
        
        pygame.draw.rect(self.screen, GREEN, corner_btn)
        pygame.draw.rect(self.screen, BLACK, corner_btn, 2)
        pygame.draw.rect(self.screen, BLUE, random_btn)
        pygame.draw.rect(self.screen, BLACK, random_btn, 2)
        pygame.draw.rect(self.screen, (255, 165, 0), manual_btn)
        pygame.draw.rect(self.screen, BLACK, manual_btn, 2)
        
        corner_text = self.font.render("Corner Start", True, BLACK)
        random_text = self.font.render("Random Start", True, BLACK)
        manual_text = self.font.render("Place Manually", True, BLACK)
        
        corner_rect = corner_text.get_rect(center=corner_btn.center)
        random_rect = random_text.get_rect(center=random_btn.center)
        manual_rect = manual_text.get_rect(center=manual_btn.center)
        
        self.screen.blit(corner_text, corner_rect)
        self.screen.blit(random_text, random_rect)
        self.screen.blit(manual_text, manual_rect)
        
        # Preview grid
        preview_x = 550
        preview_y = 200
        preview_size = 15
        
        for x in range(min(self.grid_width, 12)):
            for y in range(min(self.grid_height, 8)):
                cell_x = preview_x + x * preview_size
                cell_y = preview_y + y * preview_size
                
                color = LIGHT_GREEN if (x + y) % 2 == 0 else GREEN
                pygame.draw.rect(self.screen, color, 
                               (cell_x, cell_y, preview_size, preview_size))
                pygame.draw.rect(self.screen, BLACK, 
                               (cell_x, cell_y, preview_size, preview_size), 1)
        
        # Instructions
        instruction_text = "Use buttons to configure, then click a starting method. Press M for Main Menu."
        instruction_surface = self.small_font.render(instruction_text, True, BLACK)
        instruction_rect = instruction_surface.get_rect(center=(500, 450))
        self.screen.blit(instruction_surface, instruction_rect)
    
    def draw_placement_screen(self):
        """Draw manual placement screen."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        LIGHT_GREEN = (144, 238, 144)
        GREEN = (100, 200, 100)
        
        # Title
        title = f"Place Explorer {self.placing_player + 1} of {self.num_players}"
        title_text = self.large_font.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(500, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw grid
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        grid_x = (1000 - grid_width) // 2
        grid_y = 100
        
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_x = grid_x + x * self.cell_size
                cell_y = grid_y + y * self.cell_size
                
                color = LIGHT_GREEN if (x + y) % 2 == 0 else GREEN
                pygame.draw.rect(self.screen, color, 
                               (cell_x, cell_y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, BLACK, 
                               (cell_x, cell_y, self.cell_size, self.cell_size), 1)
        
        # Draw placed players
        for player in self.players:
            cell_x = grid_x + player.x * self.cell_size
            cell_y = grid_y + player.y * self.cell_size
            center_x = cell_x + self.cell_size // 2
            center_y = cell_y + self.cell_size // 2
            
            radius = min(15, self.cell_size // 3)
            pygame.draw.circle(self.screen, player.color, (center_x, center_y), radius)
            pygame.draw.circle(self.screen, BLACK, (center_x, center_y), radius, 2)
    
    def draw_game_screen(self):
        """Draw main game screen."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        LIGHT_GREEN = (144, 238, 144)
        GREEN = (100, 200, 100)
        YELLOW = (255, 255, 100)
        BLUE = (100, 150, 255)
        RED = (255, 100, 100)
        GRAY = (150, 150, 150)
        
        # Title
        title = f"Advanced Explorer Team - {self.grid_width}×{self.grid_height} Grid"
        title_text = self.large_font.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(500, 30))
        self.screen.blit(title_text, title_rect)
        
        # Calculate grid position
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        grid_x = (1000 - grid_width) // 2
        grid_y = 70
        
        # Draw grid
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_x = grid_x + x * self.cell_size
                cell_y = grid_y + y * self.cell_size
                
                color = LIGHT_GREEN if (x + y) % 2 == 0 else GREEN
                pygame.draw.rect(self.screen, color, 
                               (cell_x, cell_y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, BLACK, 
                               (cell_x, cell_y, self.cell_size, self.cell_size), 1)
        
        # Draw players
        for player in self.players:
            cell_x = grid_x + player.x * self.cell_size
            cell_y = grid_y + player.y * self.cell_size
            center_x = cell_x + self.cell_size // 2
            center_y = cell_y + self.cell_size // 2
            
            radius = min(15, self.cell_size // 3)
            pygame.draw.circle(self.screen, player.color, (center_x, center_y), radius)
            pygame.draw.circle(self.screen, BLACK, (center_x, center_y), radius, 2)
            
            # Show group membership with connecting lines
            if player.found:
                pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), radius + 3, 2)
        
        # Draw group connections
        for group in self.player_groups:
            if len(group) > 1:
                # Draw lines between group members
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        p1 = self.players[group[i]]
                        p2 = self.players[group[j]]
                        
                        if p1.x == p2.x and p1.y == p2.y:  # Same position
                            x1 = grid_x + p1.x * self.cell_size + self.cell_size // 2
                            y1 = grid_y + p1.y * self.cell_size + self.cell_size // 2
                            pygame.draw.circle(self.screen, YELLOW, (x1, y1), 25, 3)
        
        # Player statistics
        stats_y = grid_y + grid_height + 20
        for i, player in enumerate(self.players):
            status = "TOGETHER" if player.found else f"Searching ({player.moves} moves)"
            color = GREEN if player.found else BLACK
            
            player_text = f"{player.name}: {status}"
            text = pygame.font.Font(None, 20).render(player_text, True, color)
            x_pos = 50 + (i % 2) * 400
            y_pos = stats_y + (i // 2) * 25
            self.screen.blit(text, (x_pos, y_pos))
        
        # Group information
        if self.player_groups:
            group_y = stats_y + 60
            group_text = f"Active Groups: {len(self.player_groups)}"
            text = self.font.render(group_text, True, BLACK)
            self.screen.blit(text, (50, group_y))
            
            for i, group in enumerate(self.player_groups):
                member_names = [self.players[pid].name.split()[1] for pid in group if pid < len(self.players)]
                group_desc = f"Group {i+1}: {', '.join(member_names)} ({len(group)} members)"
                text = pygame.font.Font(None, 18).render(group_desc, True, GREEN)
                self.screen.blit(text, (70, group_y + 25 + i * 20))
        
        # Game statistics
        stats = self.stats.get_summary()
        if stats:
            summary_y = stats_y + 120
            summary_text = f"Games: {stats['total_runs']} | Average moves: {stats['average_moves']:.1f} | Best: {stats.get('shortest_run', 0)}"
            text = pygame.font.Font(None, 20).render(summary_text, True, BLACK)
            text_rect = text.get_rect(center=(500, summary_y))
            self.screen.blit(text, text_rect)
        
        # Control buttons
        pause_color = GRAY if self.paused else BLUE
        pygame.draw.rect(self.screen, pause_color, pygame.Rect(50, 600, 80, 30))
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(50, 600, 80, 30), 2)
        
        pygame.draw.rect(self.screen, RED, pygame.Rect(140, 600, 80, 30))
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(140, 600, 80, 30), 2)
        
        pygame.draw.rect(self.screen, GREEN, pygame.Rect(230, 600, 100, 30))
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(230, 600, 100, 30), 2)
        
        pause_text = self.font.render("PAUSE" if not self.paused else "PLAY", True, BLACK)
        reset_text = self.font.render("RESET", True, BLACK)
        setup_text = self.font.render("NEW SETUP", True, BLACK)
        
        pause_rect = pause_text.get_rect(center=(90, 615))
        reset_rect = reset_text.get_rect(center=(180, 615))
        setup_rect = setup_text.get_rect(center=(280, 615))
        
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(reset_text, reset_rect)
        self.screen.blit(setup_text, setup_rect)
        
        # Status message
        if self.game_over:
            status = f"🎉 All {self.num_players} explorers united! Excellent teamwork! 🎉"
            color = GREEN
        elif self.paused:
            status = "⏸️ Exploration paused"
            color = GRAY
        else:
            groups_count = len(self.player_groups)
            solo_count = self.num_players - sum(len(group) for group in self.player_groups)
            status = f"🔍 {groups_count} groups formed, {solo_count} still searching alone..."
            color = BLACK
        
        status_text = self.font.render(status, True, color)
        status_rect = status_text.get_rect(center=(500, 670))
        self.screen.blit(status_text, status_rect)
        
        # Control instructions
        control_text = "SPACE: Pause/Resume | R: Reset | M: Main Menu | ESC: Exit"
        control_surface = self.small_font.render(control_text, True, BLACK)
        control_rect = control_surface.get_rect(center=(500, 720))
        self.screen.blit(control_surface, control_rect)

class Grades68Game:
    """Grades 6-8: Full game control PLUS experiments, protocols, and data analysis."""
    
    def __init__(self, screen: pygame.Surface, audio: AudioManager):
        self.screen = screen
        self.audio = audio
        
        # Main mode: game (interactive play) or research (experiments)
        self.mode = "menu"  # menu, game_setup, game_play, research_mode
        
        # Game components (like grades 3-5 but enhanced)
        self.grid_width = 8
        self.grid_height = 6
        self.num_players = 2
        self.cell_size = 50
        
        # Game state
        self.grid = None
        self.players = []
        self.player_groups = []
        self.paused = False
        self.game_over = False
        self.move_timer = 0
        self.move_interval = 500
        self.stats = GameStatistics()
        
        # Movement protocol (NEW for 6-8!)
        self.movement_protocol = "random"  # random, systematic, biased_north, spiral
        
        # Research/Experiment features
        self.experiment_data = []
        self.research_state = "design"  # design, running, analysis
        self.num_trials = 3
        self.current_trial = 0
        self.current_experiment = None
        
        # Available protocols
        self.protocols = {
            "random": "Random Movement",
            "systematic": "Systematic Search", 
            "biased_north": "Biased North",
            "spiral": "Spiral Pattern"
        }
        
        # UI
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 32)
        
        self.audio.speak("Welcome to Advanced Forest Research! You have full control like grades 3-5, PLUS you can test different movement protocols and run experiments!")
    
    def handle_event(self, event) -> bool:
        """Handle user input events."""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                elif self.mode == "menu":
                    if event.key == pygame.K_1:
                        self.mode = "game_setup"
                        self.audio.speak("Setting up interactive game. Configure your forest and explorers!")
                    elif event.key == pygame.K_2:
                        self.mode = "research_mode"
                        self.research_state = "design"
                        self.audio.speak("Entering research mode. Design experiments to test movement protocols!")
                    
                elif self.mode == "game_setup":
                    if event.key == pygame.K_s:
                        self.start_interactive_game()
                    elif event.key == pygame.K_m:
                        self.mode = "menu"
                        
                elif self.mode == "game_play":
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_p:
                        self.cycle_protocol()
                    elif event.key == pygame.K_m:
                        self.mode = "menu"
                        
                elif self.mode == "research_mode":
                    if self.research_state == "design":
                        if event.key == pygame.K_r:
                            self.start_research_experiment()
                        elif event.key == pygame.K_m:
                            self.mode = "menu"
                    elif self.research_state == "running":
                        if event.key == pygame.K_SPACE:
                            self.advance_research()
                    elif self.research_state == "analysis":
                        if event.key == pygame.K_m:
                            self.mode = "menu"
                        elif event.key == pygame.K_d:
                            self.research_state = "design"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.mode == "game_setup":
                    self.handle_game_setup_click(event.pos)
                elif self.mode == "research_mode" and self.research_state == "design":
                    self.handle_research_setup_click(event.pos)
            
            return True
            
        except Exception as e:
            print(f"Error in Grades68Game.handle_event: {e}")
            return True
    
    def handle_game_setup_click(self, pos):
        """Handle clicks during game setup (like grades 3-5 but with protocol selection)."""
        # Grid size controls
        if pygame.Rect(200, 200, 30, 30).collidepoint(pos) and self.grid_width > 4:
            self.grid_width -= 1
        elif pygame.Rect(270, 200, 30, 30).collidepoint(pos) and self.grid_width < 20:
            self.grid_width += 1
        elif pygame.Rect(200, 250, 30, 30).collidepoint(pos) and self.grid_height > 3:
            self.grid_height -= 1
        elif pygame.Rect(270, 250, 30, 30).collidepoint(pos) and self.grid_height < 15:
            self.grid_height += 1
        
        # Player count
        elif pygame.Rect(200, 300, 30, 30).collidepoint(pos) and self.num_players > 2:
            self.num_players -= 1
        elif pygame.Rect(270, 300, 30, 30).collidepoint(pos) and self.num_players < 4:
            self.num_players += 1
        
        # Movement protocol selection (NEW!)
        elif pygame.Rect(400, 200, 200, 30).collidepoint(pos):
            self.cycle_protocol()
        
        # Start game buttons
        elif pygame.Rect(400, 350, 120, 40).collidepoint(pos):
            self.start_interactive_game()

    def handle_research_setup_click(self, pos):
        """Handle clicks during research experiment setup.""" 
        # Grid size controls
        if pygame.Rect(200, 150, 30, 30).collidepoint(pos) and self.grid_width > 4:
            self.grid_width -= 1
        elif pygame.Rect(270, 150, 30, 30).collidepoint(pos) and self.grid_width < 20:
            self.grid_width += 1
        elif pygame.Rect(200, 190, 30, 30).collidepoint(pos) and self.grid_height > 4:
            self.grid_height -= 1
        elif pygame.Rect(270, 190, 30, 30).collidepoint(pos) and self.grid_height < 15:
            self.grid_height += 1
        
        # Player count
        elif pygame.Rect(200, 230, 30, 30).collidepoint(pos) and self.num_players > 2:
            self.num_players -= 1
        elif pygame.Rect(270, 230, 30, 30).collidepoint(pos) and self.num_players < 4:
            self.num_players += 1
        
        # Trial count
        elif pygame.Rect(200, 270, 30, 30).collidepoint(pos) and self.num_trials > 1:
            self.num_trials -= 1
        elif pygame.Rect(270, 270, 30, 30).collidepoint(pos) and self.num_trials < 20:
            self.num_trials += 1
        
        # Protocol selection
        elif pygame.Rect(400, 150, 200, 30).collidepoint(pos):
            self.cycle_protocol()
        
        # Start experiment
        elif pygame.Rect(400, 300, 150, 40).collidepoint(pos):
            self.start_research_experiment()
    
    def cycle_protocol(self):
        """Cycle through available movement protocols."""
        protocol_list = list(self.protocols.keys())
        current_index = protocol_list.index(self.movement_protocol)
        next_index = (current_index + 1) % len(protocol_list)
        self.movement_protocol = protocol_list[next_index]
        self.audio.speak(f"Selected {self.protocols[self.movement_protocol]} protocol")
    
    def start_interactive_game(self):
        """Start the interactive game (like grades 3-5 but with selectable protocols)."""
        self.grid = Grid(self.grid_width, self.grid_height)
        self.mode = "game_play"
        self.paused = False
        self.game_over = False
        
        # Create players at corners
        colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 165, 0)]
        names = ["Explorer 1", "Explorer 2", "Explorer 3", "Explorer 4"]
        
        positions = [(0, 0), (self.grid_width-1, self.grid_height-1), 
                    (0, self.grid_height-1), (self.grid_width-1, 0)]
        
        self.players = []
        self.player_groups = []
        
        for i in range(self.num_players):
            x, y = positions[i]
            player = Player(x, y, colors[i], names[i], i)
            self.players.append(player)
        
        self.stats.start_run()
        self.audio.speak(f"Game started with {self.protocols[self.movement_protocol]} movement protocol! Press P to change protocols during play.")
    
    def start_research_experiment(self):
        """Start a research experiment."""
        self.research_state = "running"
        self.current_trial = 0
        self.current_experiment = {
            'protocol': self.movement_protocol,
            'grid_size': (self.grid_width, self.grid_height),
            'num_players': self.num_players,
            'trials': []
        }
        
        self.audio.speak(f"Starting research experiment: testing {self.protocols[self.movement_protocol]} on {self.grid_width}x{self.grid_height} grid")
    
    def advance_research(self):
        """Advance the research experiment."""
        if self.current_trial < self.num_trials:
            trial_result = self.run_trial()
            self.current_experiment['trials'].append(trial_result)
            self.current_trial += 1
            
            self.audio.speak(f"Trial {self.current_trial} complete: {trial_result['moves']} moves")
            
            if self.current_trial >= self.num_trials:
                self.experiment_data.append(self.current_experiment)
                self.research_state = "analysis"
                avg_moves = sum(t['moves'] for t in self.current_experiment['trials']) / len(self.current_experiment['trials'])
                self.audio.speak(f"Experiment complete! Average: {avg_moves:.1f} moves")
    
    def reset_game(self):
        """Reset the current game."""
        if self.players:
            positions = [(0, 0), (self.grid_width-1, self.grid_height-1), 
                        (0, self.grid_height-1), (self.grid_width-1, 0)]
            
            for i, player in enumerate(self.players):
                x, y = positions[i]
                player.x, player.y = x, y
                player.moves = 0
                player.found = False
            
            self.player_groups = []
            self.paused = False
            self.game_over = False
            self.stats.start_run()
    
    def run_trial(self):
        """Run a single trial for research mode."""
        # Create a test grid and players
        test_grid = Grid(self.grid_width, self.grid_height)
        test_players = []
        
        colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 165, 0)]
        names = ["Test 1", "Test 2", "Test 3", "Test 4"]
        positions = [(0, 0), (self.grid_width-1, self.grid_height-1), 
                    (0, self.grid_height-1), (self.grid_width-1, 0)]
        
        for i in range(self.num_players):
            x, y = positions[i]
            player = Player(x, y, colors[i], names[i], i)
            test_players.append(player)
        
        moves = 0
        max_moves = self.grid_width * self.grid_height * 10  # Safety limit
        
        while not test_grid.all_visited() and moves < max_moves:
            # Move all players according to protocol
            for player in test_players:
                old_x, old_y = player.x, player.y
                new_x, new_y = self.apply_movement_protocol_test(player, test_grid, moves)
                
                # Ensure movement is valid
                if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
                    player.x, player.y = new_x, new_y
                    test_grid.visit(new_x, new_y)
            
            moves += 1
        
        return {
            'moves': moves,
            'completed': test_grid.all_visited(),
            'protocol': self.movement_protocol,
            'grid_size': (self.grid_width, self.grid_height)
        }
    
    def apply_movement_protocol_test(self, player, grid, move_count):
        """Apply movement protocol for testing (similar to apply_movement_protocol)."""
        if self.movement_protocol == "random":
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            dx, dy = random.choice(directions)
            return player.x + dx, player.y + dy
            
        elif self.movement_protocol == "systematic":
            # Systematic grid search (right-first, then down, then wrap)
            new_x = player.x + 1
            if new_x >= self.grid_width:
                new_x = 0
                new_y = player.y + 1
                if new_y >= self.grid_height:
                    new_y = 0
            else:
                new_y = player.y
            return new_x, new_y
            
        elif self.movement_protocol == "biased_north":
            # 60% chance north, 40% chance random other direction
            if random.random() < 0.6 and player.y > 0:
                return player.x, player.y - 1
            else:
                directions = [(0, 1), (1, 0), (-1, 0)]
                dx, dy = random.choice(directions)
                return player.x + dx, player.y + dy
                
        elif self.movement_protocol == "spiral":
            # Simple spiral pattern from center
            cx, cy = self.grid_width // 2, self.grid_height // 2
            dx, dy = player.x - cx, player.y - cy
            
            # Rotate 90 degrees clockwise
            new_dx, new_dy = -dy, dx
            return cx + new_dx, cy + new_dy
            
        return player.x, player.y  # Fallback
    
    def start_experiment(self):
        """Start a new experiment with current parameters."""
        self.state = "running_experiment"
        self.current_trial = 0
        self.current_experiment = {
            'protocol': self.movement_protocol,
            'grid_size': (self.grid_width, self.grid_height),
            'num_players': self.num_players,
            'trials': []
        }
        
        self.audio.speak(f"Starting experiment with {self.movement_protocol} protocol. {self.num_trials} trials on {self.grid_width} by {self.grid_height} grid.")
    
    def advance_experiment(self):
        """Run the next trial or finish experiment."""
        if self.current_trial < self.num_trials:
            # Run actual trial with real game mechanics
            self.audio.speak(f"Running trial {self.current_trial + 1} with {self.movement_protocol} protocol...")
            trial_result = self.simulate_trial()
            self.current_experiment['trials'].append(trial_result)
            self.current_trial += 1
            
            # Announce trial result
            if trial_result['success']:
                self.audio.speak(f"Trial {trial_result['trial']} complete: {trial_result['moves']} moves in {trial_result['duration']:.1f} seconds")
            else:
                self.audio.speak(f"Trial {trial_result['trial']} timed out - maximum moves reached")
            
            if self.current_trial >= self.num_trials:
                # Experiment complete - analyze results
                successful_trials = [t for t in self.current_experiment['trials'] if t['success']]
                if successful_trials:
                    avg_moves = sum(t['moves'] for t in successful_trials) / len(successful_trials)
                    avg_time = sum(t['duration'] for t in successful_trials) / len(successful_trials)
                    success_rate = len(successful_trials) / len(self.current_experiment['trials']) * 100
                    
                    self.experiment_data.append(self.current_experiment)
                    self.audio.speak(f"Experiment complete! Success rate: {success_rate:.0f}%, Average moves: {avg_moves:.1f}, Average time: {avg_time:.1f} seconds")
                else:
                    self.audio.speak("Experiment complete but no successful trials - protocol may be ineffective for this grid size")
                    self.experiment_data.append(self.current_experiment)
                
                self.state = "data_analysis"
        
    def simulate_trial(self):
        """Run an actual trial with the current protocol."""
        # Create a mini-game engine for the experiment
        grid = Grid(self.grid_width, self.grid_height)
        
        # Create players with different starting positions
        colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 165, 0)]
        names = ["Exp1", "Exp2", "Exp3", "Exp4"]
        
        players = []
        for i in range(self.num_players):
            # Place at corners for consistency
            if i == 0:
                x, y = 0, 0
            elif i == 1:
                x, y = self.grid_width - 1, self.grid_height - 1
            elif i == 2:
                x, y = 0, self.grid_height - 1
            else:
                x, y = self.grid_width - 1, 0
                
            player = Player(x, y, colors[i], names[i], i)
            players.append(player)
        
        # Run the trial using the selected protocol
        moves = 0
        max_moves = self.grid_width * self.grid_height * 10  # Prevent infinite loops
        
        start_time = time.time()
        
        while moves < max_moves:
            moves += 1
            
            # Move players according to protocol
            for player in players:
                if self.movement_protocol == "random":
                    player.move_random(grid)
                elif self.movement_protocol == "systematic":
                    self.move_systematic(player, grid, moves)
                elif self.movement_protocol == "biased_north":
                    self.move_biased_north(player, grid)
                elif self.movement_protocol == "spiral":
                    self.move_spiral(player, grid, moves)
            
            # Check if all players have met
            if self.all_players_met(players):
                break
        
        duration = time.time() - start_time
        
        return {
            'trial': self.current_trial + 1,
            'moves': moves,
            'duration': duration,
            'protocol': self.movement_protocol,
            'grid_size': (self.grid_width, self.grid_height),
            'success': moves < max_moves
        }
    
    def move_systematic(self, player, grid, moves):
        """Systematic grid search pattern."""
        # Move in a systematic pattern: left-to-right, top-to-bottom
        target_x = (moves - 1) % grid.width
        target_y = ((moves - 1) // grid.width) % grid.height
        
        if player.x < target_x:
            if grid.is_valid_position(player.x + 1, player.y):
                player.x += 1
                player.moves += 1
        elif player.x > target_x:
            if grid.is_valid_position(player.x - 1, player.y):
                player.x -= 1
                player.moves += 1
        elif player.y < target_y:
            if grid.is_valid_position(player.x, player.y + 1):
                player.y += 1
                player.moves += 1
        elif player.y > target_y:
            if grid.is_valid_position(player.x, player.y - 1):
                player.y -= 1
                player.moves += 1
    
    def move_biased_north(self, player, grid):
        """Biased movement preferring north direction."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # North first
        
        for dx, dy in directions:
            new_x, new_y = player.x + dx, player.y + dy
            if grid.is_valid_position(new_x, new_y):
                # 60% chance to go north if possible, otherwise random
                if dy == -1 and random.random() < 0.6:
                    player.x, player.y = new_x, new_y
                    player.moves += 1
                    return
                elif dy != -1 and random.random() < 0.3:
                    player.x, player.y = new_x, new_y
                    player.moves += 1
                    return
        
        # Fallback to random if no bias move works
        player.move_random(grid)
    
    def move_spiral(self, player, grid, moves):
        """Spiral search pattern from center outward."""
        center_x = grid.width // 2
        center_y = grid.height // 2
        
        # Calculate spiral position based on moves
        spiral_radius = (moves // 8) + 1
        angle_step = moves % 8
        
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        
        if angle_step < len(directions):
            dx, dy = directions[angle_step]
            target_x = center_x + dx * spiral_radius
            target_y = center_y + dy * spiral_radius
            
            # Move toward spiral target
            if target_x < 0: target_x = 0
            if target_x >= grid.width: target_x = grid.width - 1
            if target_y < 0: target_y = 0
            if target_y >= grid.height: target_y = grid.height - 1
            
            # Move one step toward target
            if player.x < target_x and grid.is_valid_position(player.x + 1, player.y):
                player.x += 1
                player.moves += 1
            elif player.x > target_x and grid.is_valid_position(player.x - 1, player.y):
                player.x -= 1
                player.moves += 1
            elif player.y < target_y and grid.is_valid_position(player.x, player.y + 1):
                player.y += 1
                player.moves += 1
            elif player.y > target_y and grid.is_valid_position(player.x, player.y - 1):
                player.y -= 1
                player.moves += 1
            else:
                player.move_random(grid)
        else:
            player.move_random(grid)
    
    def all_players_met(self, players):
        """Check if all players are at the same position."""
        if len(players) <= 1:
            return True
        
        first_pos = (players[0].x, players[0].y)
        return all((p.x, p.y) == first_pos for p in players)
    
    def run_quick_comparison(self):
        """Run a quick comparison of all protocols."""
        self.audio.speak("Running quick protocol comparison...")
        
        for protocol in self.protocols.keys():
            self.movement_protocol = protocol
            experiment = {
                'protocol': protocol,
                'grid_size': (self.grid_width, self.grid_height),
                'num_players': self.num_players,
                'trials': []
            }
            
            # Run 3 quick trials
            for i in range(3):
                trial_result = self.simulate_trial()
                experiment['trials'].append(trial_result)
            
            self.experiment_data.append(experiment)
        
        self.state = "data_analysis"
        self.audio.speak("Comparison complete! Analyzing results...")
    
    def start_live_experiment(self):
        """Start a live experiment demonstration."""
        try:
            self.state = "live_experiment"
            self.live_grid = Grid(8, 6)  # Standard demo size
            self.live_players = []
            self.live_moves = 0
            self.live_protocol = "random"
            self.live_max_moves = 200
            self.live_timer = 0
            
            # Create demo players
            colors = [(255, 100, 100), (100, 100, 255)]
            names = ["Alpha", "Beta"]
            
            self.live_players = [
                Player(0, 0, colors[0], names[0], 0),
                Player(7, 5, colors[1], names[1], 1)
            ]
            
            self.audio.speak("Starting live experiment demonstration. Watch the protocols in action!")
        except Exception as e:
            print(f"Error starting live experiment: {e}")
            self.state = "menu"
    
    def update(self, dt: int):
        """Update game state."""
        if self.research_state == "running":
            # Auto-advance research every 2 seconds
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time > 2000:
                self.advance_research()
                self.last_move_time = current_time
                
        elif self.mode == "game_play" and not self.paused and not self.game_over:
            # Update interactive game (like grades 3-5)
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time > 500:  # Move every 500ms
                self.move_all_players()
                self.last_move_time = current_time
                
                # Check if all grid visited
                if self.grid.all_visited():
                    self.game_over = True
                    total_moves = sum(player.moves for player in self.players)
                    self.stats.end_run(total_moves)
                    self.audio.speak(f"Grid complete! Total moves: {total_moves}")
        

    
    def draw(self):
        """Draw the 6-8 interface."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        GREEN = (100, 200, 100)
        RED = (255, 100, 100)
        GRAY = (150, 150, 150)
        
        try:
            self.screen.fill(WHITE)
            
            if self.mode == "menu":
                self.draw_main_menu()
            elif self.mode == "game_setup":
                self.draw_game_setup()
            elif self.mode == "game_play":
                self.draw_game_play()
            elif self.mode == "research_setup":
                self.draw_research_setup()
            elif self.mode == "research_mode":
                self.draw_research_mode()
            else:
                # Fallback to menu if unknown mode
                self.mode = "menu"
                self.draw_main_menu()
        
        except Exception as e:
            print(f"Error in Grades68Game.draw: {e}")
            # Fallback - just show a basic error screen
            self.screen.fill(WHITE)
            error_text = f"Graphics Error: {str(e)}"
            if hasattr(self, 'font'):
                text = self.font.render(error_text, True, BLACK)
                text_rect = text.get_rect(center=(500, 350))
                self.screen.blit(text, text_rect)
    
    def draw_game_setup(self):
        """Draw interactive game setup screen."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        GREEN = (100, 200, 100)
        
        title_text = self.font.render("Grades 6-8: Interactive Exploration Game", True, BLACK)
        title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Grid size controls
        grid_text = self.font.render(f"Grid Size: {self.grid_width} x {self.grid_height}", True, BLACK)
        self.screen.blit(grid_text, (50, 120))
        
        # Player count controls
        player_text = self.font.render(f"Players: {self.num_players}", True, BLACK)
        self.screen.blit(player_text, (50, 160))
        
        # Movement protocol
        protocol_text = self.font.render(f"Protocol: {self.protocols[self.movement_protocol]}", True, BLACK)
        self.screen.blit(protocol_text, (50, 200))
        
        # Instructions
        instructions = [
            "W/S: Adjust grid width    A/D: Adjust grid height",
            "↑/↓: Adjust player count  P: Change protocol",
            "SPACE: Start Interactive Game    M: Main Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (50, 280 + i*30))
    
    def draw_game_play(self):
        """Draw the interactive game in progress."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        GREEN = (100, 200, 100)
        RED = (255, 100, 100)
        
        # Draw grid
        if hasattr(self, 'grid') and self.grid:
            cell_size = min(400 // max(self.grid_width, self.grid_height), 40)
            start_x = (self.screen.get_width() - self.grid_width * cell_size) // 2
            start_y = 100
            
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    rect = pygame.Rect(start_x + x * cell_size, start_y + y * cell_size, 
                                     cell_size, cell_size)
                    
                    # Color based on visited status
                    if self.grid.is_visited(x, y):
                        pygame.draw.rect(self.screen, GREEN, rect)
                    else:
                        pygame.draw.rect(self.screen, WHITE, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            # Draw players
            if hasattr(self, 'players'):
                for player in self.players:
                    px = start_x + player.x * cell_size + cell_size // 2
                    py = start_y + player.y * cell_size + cell_size // 2
                    pygame.draw.circle(self.screen, player.color, (px, py), cell_size // 4)
        
        # Game info
        info_y = start_y + self.grid_height * cell_size + 20
        protocol_text = self.font.render(f"Protocol: {self.protocols[self.movement_protocol]}", True, BLACK)
        self.screen.blit(protocol_text, (50, info_y))
        
        if hasattr(self, 'players'):
            total_moves = sum(player.moves for player in self.players)
            moves_text = self.font.render(f"Total Moves: {total_moves}", True, BLACK)
            self.screen.blit(moves_text, (50, info_y + 30))
        
        # Controls
        controls = ["SPACE: Pause/Resume", "P: Change Protocol", "R: Reset", "M: Main Menu", "ESC: Return to Setup"]
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, BLACK)
            self.screen.blit(text, (50, info_y + 70 + i*25))
        
        if self.paused:
            pause_text = self.font.render("PAUSED", True, RED)
            pause_rect = pause_text.get_rect(center=(self.screen.get_width()//2, 50))
            self.screen.blit(pause_text, pause_rect)
        
        if self.game_over:
            win_text = self.font.render("GRID COMPLETE!", True, GREEN)
            win_rect = win_text.get_rect(center=(self.screen.get_width()//2, 50))
            self.screen.blit(win_text, win_rect)
    
    def draw_research_setup(self):
        """Draw research experiment setup screen."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        
        title_text = self.font.render("Grades 6-8: Research Mode Setup", True, BLACK)
        title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Research parameters
        trials_text = self.font.render(f"Number of trials: {self.num_trials}", True, BLACK)
        self.screen.blit(trials_text, (50, 120))
        
        protocol_text = self.font.render(f"Testing protocol: {self.protocols[self.movement_protocol]}", True, BLACK)
        self.screen.blit(protocol_text, (50, 160))
        
        grid_text = self.font.render(f"Grid size: {self.grid_width} x {self.grid_height}", True, BLACK)
        self.screen.blit(grid_text, (50, 200))
        
        # Instructions
        instructions = [
            "↑/↓: Adjust trial count    P: Change protocol",
            "W/S: Adjust grid width    A/D: Adjust grid height",
            "SPACE: Start Research    M: Main Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (50, 280 + i*30))
    
    def draw_research_mode(self):
        """Draw research experiment in progress."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        GREEN = (100, 200, 100)
        
        title_text = self.font.render("Research Experiment Running", True, BLACK)
        title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 50))
        self.screen.blit(title_text, title_rect)
        
        if hasattr(self, 'current_experiment'):
            exp = self.current_experiment
            protocol_text = self.font.render(f"Testing: {self.protocols[exp['protocol']]}", True, BLACK)
            self.screen.blit(protocol_text, (50, 120))
            
            progress_text = self.font.render(f"Trial: {self.current_trial + 1} / {self.num_trials}", True, BLACK)
            self.screen.blit(progress_text, (50, 160))
            
            if exp['trials']:
                avg_moves = sum(t['moves'] for t in exp['trials']) / len(exp['trials'])
                avg_text = self.font.render(f"Average moves so far: {avg_moves:.1f}", True, BLACK)
                self.screen.blit(avg_text, (50, 200))
        
        if self.research_state == "analysis":
            analysis_text = self.font.render("Experiment Complete - Press A for Analysis", True, GREEN)
            self.screen.blit(analysis_text, (50, 300))
    
    def draw_main_menu(self):
        """Draw main research menu."""
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        GREEN = (100, 200, 100)
        
        # Title
        title = "Forest Movement Research Laboratory - Grades 6-8"
        title_text = self.large_font.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(500, 80))
        self.screen.blit(title_text, title_rect)
        
        # Description
        desc_lines = [
            "🔬 Design controlled experiments to study movement protocols",
            "📊 Analyze how grid size and shape affect search efficiency", 
            "📈 Compare different search strategies with statistical analysis",
            "🧪 Test hypotheses about optimal wandering patterns"
        ]
        
        for i, line in enumerate(desc_lines):
            text = self.font.render(line, True, BLACK)
            text_rect = text.get_rect(center=(500, 140 + i * 30))
            self.screen.blit(text, text_rect)
        
        # Menu options
        options = [
            "1. Design Custom Experiment - Test specific protocols and parameters",
            "2. Data Analysis Lab - Review results and generate reports", 
            "3. Quick Protocol Comparison - Compare all movement strategies",
            "4. Live Protocol Demo - Watch algorithms in real-time action",
            "",
            "Research Questions to Explore:",
            "• Which protocol finds targets fastest on different grid shapes?",
            "• How does grid size affect the advantage of systematic vs random search?",
            "• What's the optimal strategy when multiple searchers are present?",
            "• How do different protocols perform under time constraints?"
        ]
        
        for i, option in enumerate(options):
            color = BLACK if not option.startswith("•") else BLUE
            font = self.font if not option.startswith("•") else pygame.font.Font(None, 20)
            text = font.render(option, True, color)
            
            if option and option[0].isdigit():
                # Highlight menu options
                text_rect = text.get_rect(center=(500, 280 + i * 35))
            else:
                text_rect = text.get_rect(center=(500, 280 + i * 25))
            
            self.screen.blit(text, text_rect)
    
    def draw_experiment_design(self):
        """Draw experiment design interface."""
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        GREEN = (100, 200, 100)
        GRAY = (200, 200, 200)
        
        # Title
        title = "Experiment Design Laboratory"
        title_text = self.large_font.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(500, 50))
        self.screen.blit(title_text, title_rect)
        
        # Parameters
        param_texts = [
            f"Grid Width: {self.grid_width}",
            f"Grid Height: {self.grid_height}", 
            f"Explorers: {self.num_players}",
            f"Trials: {self.num_trials}"
        ]
        
        y_positions = [150, 190, 230, 270]
        
        for i, (text, y) in enumerate(zip(param_texts, y_positions)):
            # Parameter label
            label = self.font.render(text, True, BLACK)
            self.screen.blit(label, (100, y))
            
            # Control buttons
            minus_btn = pygame.Rect(200, y, 30, 30)
            plus_btn = pygame.Rect(270, y, 30, 30)
            
            pygame.draw.rect(self.screen, GRAY, minus_btn)
            pygame.draw.rect(self.screen, BLACK, minus_btn, 2)
            pygame.draw.rect(self.screen, GRAY, plus_btn) 
            pygame.draw.rect(self.screen, BLACK, plus_btn, 2)
            
            minus_text = self.font.render("-", True, BLACK)
            plus_text = self.font.render("+", True, BLACK)
            self.screen.blit(minus_text, (minus_btn.x + 10, minus_btn.y + 5))
            self.screen.blit(plus_text, (plus_btn.x + 10, plus_btn.y + 5))
        
        # Protocol selection
        protocol_label = "Movement Protocol:"
        label = self.font.render(protocol_label, True, BLACK)
        self.screen.blit(label, (350, 120))
        
        protocol_btn = pygame.Rect(400, 150, 200, 30)
        pygame.draw.rect(self.screen, BLUE, protocol_btn)
        pygame.draw.rect(self.screen, BLACK, protocol_btn, 2)
        
        protocol_text = self.protocols[self.movement_protocol]
        text = pygame.font.Font(None, 20).render(protocol_text, True, BLACK)
        text_rect = text.get_rect(center=protocol_btn.center)
        self.screen.blit(text, text_rect)
        
        # Start button
        start_btn = pygame.Rect(400, 300, 150, 40)
        pygame.draw.rect(self.screen, GREEN, start_btn)
        pygame.draw.rect(self.screen, BLACK, start_btn, 2)
        
        start_text = self.font.render("START EXPERIMENT", True, BLACK)
        start_rect = start_text.get_rect(center=start_btn.center)
        self.screen.blit(start_text, start_rect)
        
        # Instructions
        instructions = [
            "Click parameters to adjust experimental conditions",
            "Press R to start experiment, M to return to menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 20).render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(500, 400 + i * 25))
            self.screen.blit(text, text_rect)
    
    def draw_running_experiment(self):
        """Draw experiment in progress."""
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        GREEN = (100, 200, 100)
        
        # Title
        title = f"Running Experiment: {self.protocols[self.movement_protocol]}"
        title_text = self.large_font.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(500, 80))
        self.screen.blit(title_text, title_rect)
        
        # Progress
        progress_text = f"Trial {self.current_trial + 1} of {self.num_trials}"
        text = self.font.render(progress_text, True, BLACK)
        text_rect = text.get_rect(center=(500, 150))
        self.screen.blit(text, text_rect)
        
        # Progress bar
        bar_width = 400
        bar_height = 30
        bar_x = (1000 - bar_width) // 2
        bar_y = 180
        
        # Background
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Progress fill
        if self.num_trials > 0:
            fill_width = int(bar_width * self.current_trial / self.num_trials)
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, fill_width, bar_height))
        
        # Results so far
        if self.current_experiment and self.current_experiment['trials']:
            results_text = "Results so far:"
            text = self.font.render(results_text, True, BLACK)
            self.screen.blit(text, (200, 250))
            
            for i, trial in enumerate(self.current_experiment['trials'][-5:]):  # Show last 5
                trial_text = f"Trial {trial['trial']}: {trial['moves']} moves"
                text = pygame.font.Font(None, 20).render(trial_text, True, BLACK)
                self.screen.blit(text, (220, 280 + i * 25))
        
        # Instructions
        instruction = "Press SPACE to run next trial"
        if self.current_trial >= self.num_trials:
            instruction = "Experiment complete! Analyzing data..."
        
        text = self.font.render(instruction, True, BLACK)
        text_rect = text.get_rect(center=(500, 450))
        self.screen.blit(text, text_rect)
    
    def draw_data_analysis(self):
        """Draw data analysis screen."""
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        GREEN = (100, 200, 100)
        RED = (255, 100, 100)
        
        # Title
        title = "Research Data Analysis"
        title_text = self.large_font.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(500, 50))
        self.screen.blit(title_text, title_rect)
        
        if not self.experiment_data:
            # No data yet
            no_data_text = "No experimental data available. Run some experiments first!"
            text = self.font.render(no_data_text, True, BLACK)
            text_rect = text.get_rect(center=(500, 200))
            self.screen.blit(text, text_rect)
        else:
            # Show results summary
            summary_y = 120
            
            summary_text = f"Experiments Completed: {len(self.experiment_data)}"
            text = self.font.render(summary_text, True, BLACK)
            self.screen.blit(text, (100, summary_y))
            
            # Protocol comparison
            protocol_results = {}
            for experiment in self.experiment_data:
                protocol = experiment['protocol']
                trials = experiment['trials']
                if trials:
                    avg_moves = sum(t['moves'] for t in trials) / len(trials)
                    if protocol not in protocol_results:
                        protocol_results[protocol] = []
                    protocol_results[protocol].append(avg_moves)
            
            if protocol_results:
                comparison_y = summary_y + 50
                comparison_title = "Protocol Efficiency Comparison:"
                text = self.font.render(comparison_title, True, BLACK)
                self.screen.blit(text, (100, comparison_y))
                
                # Sort protocols by performance
                protocol_averages = {}
                for protocol, results in protocol_results.items():
                    protocol_averages[protocol] = sum(results) / len(results)
                
                sorted_protocols = sorted(protocol_averages.items(), key=lambda x: x[1])
                
                for i, (protocol, avg_moves) in enumerate(sorted_protocols):
                    rank_color = GREEN if i == 0 else BLUE if i == 1 else BLACK
                    rank_text = f"{i+1}. {self.protocols[protocol]}: {avg_moves:.1f} moves average"
                    
                    text = pygame.font.Font(None, 20).render(rank_text, True, rank_color)
                    self.screen.blit(text, (120, comparison_y + 30 + i * 25))
            
            # Detailed analysis
            analysis_y = 350
            
            # Calculate success rates
            protocol_success = {}
            for experiment in self.experiment_data:
                protocol = experiment['protocol']
                successful = sum(1 for t in experiment['trials'] if t['success'])
                total = len(experiment['trials'])
                success_rate = (successful / total * 100) if total > 0 else 0
                
                if protocol not in protocol_success:
                    protocol_success[protocol] = []
                protocol_success[protocol].append(success_rate)
            
            # Show success rates
            if protocol_success:
                success_title = "Success Rates by Protocol:"
                text = self.font.render(success_title, True, BLACK)
                self.screen.blit(text, (100, analysis_y))
                
                y_offset = 0
                for protocol, rates in protocol_success.items():
                    avg_rate = sum(rates) / len(rates)
                    rate_color = GREEN if avg_rate > 80 else BLUE if avg_rate > 60 else RED
                    rate_text = f"• {self.protocols[protocol]}: {avg_rate:.0f}% success rate"
                    
                    text = pygame.font.Font(None, 20).render(rate_text, True, rate_color)
                    self.screen.blit(text, (120, analysis_y + 25 + y_offset))
                    y_offset += 20
            
            # Research insights
            insights_y = 500
            insights = [
                "🔍 Research Insights:",
                f"• Most efficient protocol: {sorted_protocols[0][0] if sorted_protocols else 'None'}",
                f"• Performance gap: {(sorted_protocols[-1][1] - sorted_protocols[0][1]):.1f} moves difference" if len(sorted_protocols) > 1 else "",
                "• Systematic search: Consistent but slower overall performance",
                "• Spiral search: Most efficient for medium-sized grids",
                "• Biased movement: Good balance of speed and reliability",
                "• Random search: High variance, unpredictable results"
            ]
            
            for i, insight in enumerate(insights):
                if insight:  # Skip empty strings
                    color = BLUE if insight.startswith("🔍") else BLACK
                    font_size = 22 if insight.startswith("🔍") else 18
                    text = pygame.font.Font(None, font_size).render(insight, True, color)
                    self.screen.blit(text, (100, insights_y + i * 22))
        
        # Instructions
        instruction = "Press M to return to main menu"
        text = self.font.render(instruction, True, BLACK)
        text_rect = text.get_rect(center=(500, 650))
        self.screen.blit(text, text_rect)
    
    def cycle_live_protocol(self):
        """Cycle to next protocol for live demo."""
        try:
            protocols = list(self.protocols.keys())
            current_idx = protocols.index(self.live_protocol)
            self.live_protocol = protocols[(current_idx + 1) % len(protocols)]
            self.audio.speak(f"Switching to {self.protocols[self.live_protocol]} protocol")
        except Exception as e:
            print(f"Error cycling live protocol: {e}")
            self.live_protocol = "random"
    
    def reset_live_experiment(self):
        """Reset live experiment for next protocol."""
        try:
            self.live_moves = 0
            if hasattr(self, 'live_players') and len(self.live_players) >= 2:
                self.live_players[0].x, self.live_players[0].y = 0, 0
                self.live_players[1].x, self.live_players[1].y = 7, 5
                self.live_players[0].moves = 0
                self.live_players[1].moves = 0
        except Exception as e:
            print(f"Error resetting live experiment: {e}")
            # Recreate players if needed
            if not hasattr(self, 'live_players'):
                colors = [(255, 100, 100), (100, 100, 255)]
                names = ["Alpha", "Beta"]
                self.live_players = [
                    Player(0, 0, colors[0], names[0], 0),
                    Player(7, 5, colors[1], names[1], 1)
                ]
    
    def draw_live_experiment(self):
        """Draw live experiment visualization."""
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        LIGHT_GREEN = (144, 238, 144)
        GREEN = (100, 200, 100)
        BLUE = (100, 150, 255)
        YELLOW = (255, 255, 100)
        
        self.screen.fill(WHITE)
        
        # Title
        title = f"Live Protocol Demonstration: {self.protocols[self.live_protocol]}"
        title_text = self.large_font.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(500, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw grid
        cell_size = 60
        grid_width = self.live_grid.width * cell_size
        grid_height = self.live_grid.height * cell_size
        grid_x = (1000 - grid_width) // 2
        grid_y = 120
        
        for x in range(self.live_grid.width):
            for y in range(self.live_grid.height):
                cell_x = grid_x + x * cell_size
                cell_y = grid_y + y * cell_size
                
                color = LIGHT_GREEN if (x + y) % 2 == 0 else GREEN
                pygame.draw.rect(self.screen, color, 
                               (cell_x, cell_y, cell_size, cell_size))
                pygame.draw.rect(self.screen, BLACK, 
                               (cell_x, cell_y, cell_size, cell_size), 2)
        
        # Draw players
        for player in self.live_players:
            cell_x = grid_x + player.x * cell_size
            cell_y = grid_y + player.y * cell_size
            center_x = cell_x + cell_size // 2
            center_y = cell_y + cell_size // 2
            
            radius = 20
            pygame.draw.circle(self.screen, player.color, (center_x, center_y), radius)
            pygame.draw.circle(self.screen, BLACK, (center_x, center_y), radius, 3)
            
            # Show player trail
            for i in range(max(0, player.moves - 5), player.moves):
                trail_alpha = int(255 * (i / max(player.moves, 1)))
                trail_color = (*player.color, trail_alpha)
        
        # Stats
        stats_y = grid_y + grid_height + 30
        
        move_text = f"Total Moves: {self.live_moves}"
        protocol_text = f"Current Protocol: {self.protocols[self.live_protocol]}"
        
        move_surface = self.font.render(move_text, True, BLACK)
        protocol_surface = self.font.render(protocol_text, True, BLUE)
        
        self.screen.blit(move_surface, (200, stats_y))
        self.screen.blit(protocol_surface, (200, stats_y + 30))
        
        # Protocol description
        descriptions = {
            "random": "Players move randomly in any valid direction",
            "systematic": "Players follow a systematic grid search pattern",
            "biased_north": "Players prefer moving north, with some randomness",
            "spiral": "Players move in an expanding spiral from grid center"
        }
        
        desc_text = descriptions.get(self.live_protocol, "")
        desc_surface = pygame.font.Font(None, 20).render(desc_text, True, BLACK)
        self.screen.blit(desc_surface, (200, stats_y + 60))
        
        # Instructions
        instruction = "Watch protocols in action! Press M to return to menu"
        text = self.font.render(instruction, True, BLACK)
        text_rect = text.get_rect(center=(500, 620))
        self.screen.blit(text, text_rect)


class MainApplication:
    """Main application class that manages the entire game."""
    
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        # Set up the display
        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("Wandering in the Woods - Educational Simulation")
        
        # Set up the clock for frame rate
        self.clock = pygame.time.Clock()
        
        # Initialize audio
        self.audio_manager = AudioManager()
        
        # Game state
        self.running = True
        self.current_state = "grade_selection"
        self.current_game = None
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHT_GREEN = (144, 238, 144)
        self.DARK_GREEN = (0, 100, 0)
        self.BLUE = (100, 150, 255)
        self.GREEN = (100, 200, 100)
        self.RED = (255, 100, 100)
        self.YELLOW = (255, 255, 100)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 20)
        
        # Menu buttons
        self.menu_buttons = [
            {"text": "K-2: Simple Forest Adventure", "grade": "K2", "color": self.YELLOW, "rect": pygame.Rect(250, 200, 500, 60)},
            {"text": "3-5: Advanced Explorer Team", "grade": "3-5", "color": self.GREEN, "rect": pygame.Rect(250, 280, 500, 60)},
            {"text": "6-8: Research & Data Analysis", "grade": "6-8", "color": self.BLUE, "rect": pygame.Rect(250, 360, 500, 60)},
            {"text": "Exit Application", "grade": "quit", "color": self.RED, "rect": pygame.Rect(250, 440, 500, 60)}
        ]
        
        print("🎮 Wandering in the Woods - Educational Simulation Started!")
        print("📚 This simulation teaches computational thinking through interactive observation")
        print("🎯 Students make choices and see how their decisions affect outcomes")
        print("🔊 Audio announcements guide learning (install pyttsx3 for full audio)")
        
        # Welcome message
        self.audio_manager.speak("Welcome to Wandering in the Woods! This educational simulation will help you learn about computational thinking, problem solving, and data analysis.")
    
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60)  # 60 FPS
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self._handle_event(event)
            
            # Update
            self._update(dt)
            
            # Draw
            self._draw()
            
            pygame.display.flip()
        
        pygame.quit()
        print("👋 Thank you for exploring computational thinking with Wandering in the Woods!")
    
    def _handle_event(self, event):
        """Handle pygame events based on current state."""
        if self.current_state == "grade_selection":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_menu_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self._start_grade_level("K2")
                elif event.key == pygame.K_2:
                    self._start_grade_level("3-5")
                elif event.key == pygame.K_3:
                    self._start_grade_level("6-8")
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.running = False
        
        elif self.current_state == "game" and self.current_game:
            # Let the current game handle the event
            if not self.current_game.handle_event(event):
                # Game wants to return to menu
                self._return_to_grade_selection()
    
    def _handle_menu_click(self, pos):
        """Handle mouse clicks on menu buttons."""
        for button in self.menu_buttons:
            if button["rect"].collidepoint(pos):
                if button["grade"] == "quit":
                    self.running = False
                else:
                    self._start_grade_level(button["grade"])
                break
    
    def _start_grade_level(self, grade: str):
        """Start the selected grade level game."""
        try:
            if grade == "K2":
                self.current_game = K2Game(self.screen, self.audio_manager)
            elif grade == "3-5":
                self.current_game = Grades35Game(self.screen, self.audio_manager)
            elif grade == "6-8":
                self.current_game = Grades68Game(self.screen, self.audio_manager)
            
            if self.current_game:
                self.current_state = "game"
                print(f"🎯 Started {grade} grade level")
        
        except Exception as e:
            print(f"❌ Error starting grade level {grade}: {e}")
            self.current_state = "grade_selection"
    
    def _return_to_grade_selection(self):
        """Return to the grade level selection screen."""
        self.current_state = "grade_selection"
        self.current_game = None
        print("📋 Returned to grade level selection")
    
    def _update(self, dt: int):
        """Update the current state."""
        if self.current_state == "game" and self.current_game:
            self.current_game.update(dt)
    
    def _draw(self):
        """Draw the current state."""
        if self.current_state == "grade_selection":
            self._draw_grade_selection()
        elif self.current_state == "game" and self.current_game:
            self.current_game.draw()
        else:
            # Fallback - clear screen
            self.screen.fill(self.WHITE)
    
    def _draw_grade_selection(self):
        """Draw the grade level selection screen."""
        self.screen.fill(self.WHITE)
        
        # Title
        title = self.title_font.render("Wandering in the Woods", True, self.DARK_GREEN)
        title_rect = title.get_rect(center=(500, 80))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font.render("Educational Simulation for Computational Thinking", True, self.BLACK)
        subtitle_rect = subtitle.get_rect(center=(500, 120))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Description
        desc_lines = [
            "🎓 Interactive learning where students make choices and observe outcomes",
            "📊 Each grade level introduces progressively complex computational concepts", 
            "🧠 Develops problem-solving, pattern recognition, and analytical thinking"
        ]
        
        for i, line in enumerate(desc_lines):
            text = self.small_font.render(line, True, self.BLACK)
            text_rect = text.get_rect(center=(500, 150 + i * 20))
            self.screen.blit(text, text_rect)
        
        # Menu buttons
        for button in self.menu_buttons:
            # Button background
            pygame.draw.rect(self.screen, button["color"], button["rect"])
            pygame.draw.rect(self.screen, self.BLACK, button["rect"], 3)
            
            # Button text
            text = self.font.render(button["text"], True, self.BLACK)
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
        
        # Instructions
        instructions = [
            "Click a grade level above to start, or use keyboard shortcuts:",
            "Press 1 for K-2 | Press 2 for 3-5 | Press 3 for 6-8 | Press ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.BLACK)
            text_rect = text.get_rect(center=(500, 540 + i * 25))
            self.screen.blit(text, text_rect)


def main():
    """Main function to start the application."""
    try:
        app = MainApplication()
        app.run()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)