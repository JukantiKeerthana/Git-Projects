"""
Grades 6-8 Implementation  
Advanced version with experimental capabilities, data analysis, and multiple movement protocols.
"""

import pygame
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from typing import List, Tuple, Optional, Dict, Any
import json

from src.core.game_engine import GameEngine, Player, Grid, Position, MovementProtocol, MovementEngine
from src.core.constants import COLORS, PLAYER_COLORS, CHARACTER_NAMES, CELL_SIZE


class ExperimentDesigner:
    """Handles experimental design for testing different parameters."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Experiment parameters
        self.grid_sizes = [(3, 3), (5, 5), (7, 7), (10, 10)]
        self.protocols = [MovementProtocol.RANDOM, MovementProtocol.BIASED_NORTH, 
                         MovementProtocol.SPIRAL, MovementProtocol.SYSTEMATIC]
        self.num_players_options = [2, 3, 4]
        self.trials_per_config = 10
        
        # Current settings
        self.selected_sizes = [True] * len(self.grid_sizes)
        self.selected_protocols = [True] * len(self.protocols)
        self.selected_players = 2
        self.trials = 10
        
        # UI state
        self.buttons = self._create_buttons()
        self.experiment_ready = False
        self.cancelled = False
    
    def _create_buttons(self) -> Dict[str, pygame.Rect]:
        """Create UI buttons for the experiment designer."""
        buttons = {}
        
        # Grid size checkboxes
        for i in range(len(self.grid_sizes)):
            buttons[f'size_{i}'] = pygame.Rect(200, 150 + i * 30, 20, 20)
        
        # Protocol checkboxes  
        for i in range(len(self.protocols)):
            buttons[f'protocol_{i}'] = pygame.Rect(200, 300 + i * 30, 20, 20)
        
        # Player count controls
        buttons['players_minus'] = pygame.Rect(200, 470, 30, 25)
        buttons['players_plus'] = pygame.Rect(280, 470, 30, 25)
        
        # Trials controls
        buttons['trials_minus'] = pygame.Rect(200, 510, 30, 25)
        buttons['trials_plus'] = pygame.Rect(280, 510, 30, 25)
        
        # Action buttons
        buttons['start_experiment'] = pygame.Rect(200, 570, 120, 40)
        buttons['cancel'] = pygame.Rect(350, 570, 80, 40)
        
        return buttons
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for experiment design."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Grid size checkboxes
            for i in range(len(self.grid_sizes)):
                if self.buttons[f'size_{i}'].collidepoint(mouse_pos):
                    self.selected_sizes[i] = not self.selected_sizes[i]
                    return True
            
            # Protocol checkboxes
            for i in range(len(self.protocols)):
                if self.buttons[f'protocol_{i}'].collidepoint(mouse_pos):
                    self.selected_protocols[i] = not self.selected_protocols[i]
                    return True
            
            # Player count controls
            if self.buttons['players_minus'].collidepoint(mouse_pos) and self.selected_players > 2:
                self.selected_players -= 1
                return True
            elif self.buttons['players_plus'].collidepoint(mouse_pos) and self.selected_players < 4:
                self.selected_players += 1
                return True
            
            # Trials controls
            elif self.buttons['trials_minus'].collidepoint(mouse_pos) and self.trials > 5:
                self.trials -= 1
                return True
            elif self.buttons['trials_plus'].collidepoint(mouse_pos) and self.trials < 50:
                self.trials += 1
                return True
            
            # Action buttons
            elif self.buttons['start_experiment'].collidepoint(mouse_pos):
                if any(self.selected_sizes) and any(self.selected_protocols):
                    self.experiment_ready = True
                return True
            elif self.buttons['cancel'].collidepoint(mouse_pos):
                self.cancelled = True
                return True
        
        return False
    
    def draw(self):
        """Draw the experiment design interface."""
        # Background
        self.screen.fill(COLORS['WHITE'])
        
        # Title
        title = self.font_large.render("Design Your Experiment", True, COLORS['BLACK'])
        self.screen.blit(title, (200, 50))
        
        # Grid sizes section
        section_title = self.font_medium.render("Grid Sizes to Test:", True, COLORS['BLACK'])
        self.screen.blit(section_title, (50, 120))
        
        for i, size in enumerate(self.grid_sizes):
            y_pos = 150 + i * 30
            
            # Checkbox
            checkbox = self.buttons[f'size_{i}']
            color = COLORS['GREEN'] if self.selected_sizes[i] else COLORS['WHITE']
            pygame.draw.rect(self.screen, color, checkbox)
            pygame.draw.rect(self.screen, COLORS['BLACK'], checkbox, 2)
            
            # Label
            label = self.font_small.render(f"{size[0]} × {size[1]}", True, COLORS['BLACK'])
            self.screen.blit(label, (230, y_pos + 2))
        
        # Movement protocols section
        section_title = self.font_medium.render("Movement Protocols:", True, COLORS['BLACK'])
        self.screen.blit(section_title, (50, 270))
        
        protocol_names = ["Random", "Biased North", "Spiral", "Systematic"]
        for i, name in enumerate(protocol_names):
            y_pos = 300 + i * 30
            
            # Checkbox
            checkbox = self.buttons[f'protocol_{i}']
            color = COLORS['GREEN'] if self.selected_protocols[i] else COLORS['WHITE']
            pygame.draw.rect(self.screen, color, checkbox)
            pygame.draw.rect(self.screen, COLORS['BLACK'], checkbox, 2)
            
            # Label
            label = self.font_small.render(name, True, COLORS['BLACK'])
            self.screen.blit(label, (230, y_pos + 2))
        
        # Player count
        players_label = self.font_medium.render("Number of Players:", True, COLORS['BLACK'])
        self.screen.blit(players_label, (50, 440))
        
        # Players controls
        minus_btn = self.buttons['players_minus']
        plus_btn = self.buttons['players_plus']
        
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], minus_btn)
        pygame.draw.rect(self.screen, COLORS['BLACK'], minus_btn, 2)
        minus_text = self.font_medium.render("-", True, COLORS['BLACK'])
        self.screen.blit(minus_text, (minus_btn.x + 10, minus_btn.y + 2))
        
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], plus_btn)
        pygame.draw.rect(self.screen, COLORS['BLACK'], plus_btn, 2)
        plus_text = self.font_medium.render("+", True, COLORS['BLACK'])
        self.screen.blit(plus_text, (plus_btn.x + 10, plus_btn.y + 2))
        
        value_text = self.font_medium.render(str(self.selected_players), True, COLORS['BLACK'])
        self.screen.blit(value_text, (245, 472))
        
        # Trials per configuration
        trials_label = self.font_medium.render("Trials per Config:", True, COLORS['BLACK'])
        self.screen.blit(trials_label, (50, 480))
        
        # Trials controls
        minus_btn = self.buttons['trials_minus']
        plus_btn = self.buttons['trials_plus']
        
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], minus_btn)
        pygame.draw.rect(self.screen, COLORS['BLACK'], minus_btn, 2)
        minus_text = self.font_medium.render("-", True, COLORS['BLACK'])
        self.screen.blit(minus_text, (minus_btn.x + 10, minus_btn.y + 2))
        
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], plus_btn)
        pygame.draw.rect(self.screen, COLORS['BLACK'], plus_btn, 2)
        plus_text = self.font_medium.render("+", True, COLORS['BLACK'])
        self.screen.blit(plus_text, (plus_btn.x + 10, plus_btn.y + 2))
        
        value_text = self.font_medium.render(str(self.trials), True, COLORS['BLACK'])
        self.screen.blit(value_text, (245, 512))
        
        # Action buttons
        start_btn = self.buttons['start_experiment']
        cancel_btn = self.buttons['cancel']
        
        # Start button
        color = COLORS['GREEN'] if any(self.selected_sizes) and any(self.selected_protocols) else COLORS['GRAY']
        pygame.draw.rect(self.screen, color, start_btn)
        pygame.draw.rect(self.screen, COLORS['BLACK'], start_btn, 2)
        start_text = self.font_medium.render("START", True, COLORS['BLACK'])
        start_rect = start_text.get_rect(center=start_btn.center)
        self.screen.blit(start_text, start_rect)
        
        # Cancel button
        pygame.draw.rect(self.screen, COLORS['RED'], cancel_btn)
        pygame.draw.rect(self.screen, COLORS['BLACK'], cancel_btn, 2)
        cancel_text = self.font_medium.render("CANCEL", True, COLORS['BLACK'])
        cancel_rect = cancel_text.get_rect(center=cancel_btn.center)
        self.screen.blit(cancel_text, cancel_rect)
    
    def get_experiment_config(self) -> Dict[str, Any]:
        """Get the configured experiment parameters."""
        selected_grid_sizes = [self.grid_sizes[i] for i in range(len(self.grid_sizes)) 
                              if self.selected_sizes[i]]
        selected_movement_protocols = [self.protocols[i] for i in range(len(self.protocols))
                                     if self.selected_protocols[i]]
        
        return {
            'grid_sizes': selected_grid_sizes,
            'movement_protocols': selected_movement_protocols,
            'num_players': self.selected_players,
            'trials_per_config': self.trials
        }


class ExperimentRunner:
    """Runs experiments and collects data."""
    
    def __init__(self, config: Dict[str, Any], screen: pygame.Surface):
        self.config = config
        self.screen = screen
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Experiment state
        self.results = []
        self.current_progress = 0
        self.total_experiments = (len(config['grid_sizes']) * 
                                len(config['movement_protocols']) * 
                                config['trials_per_config'])
        
        self.running = False
        self.completed = False
        
    def run_experiments(self):
        """Run all experiments."""
        self.running = True
        self.results = []
        
        for grid_size in self.config['grid_sizes']:
            for protocol in self.config['movement_protocols']:
                for trial in range(self.config['trials_per_config']):
                    result = self._run_single_experiment(grid_size, protocol)
                    self.results.append(result)
                    self.current_progress += 1
                    
                    # Allow UI updates during long experiments
                    if self.current_progress % 5 == 0:
                        pygame.event.pump()
        
        self.running = False
        self.completed = True
    
    def _run_single_experiment(self, grid_size: Tuple[int, int], protocol: MovementProtocol) -> Dict[str, Any]:
        """Run a single experiment configuration."""
        grid = Grid(grid_size[0], grid_size[1])
        
        # Create players at random positions
        players = []
        positions = []
        
        while len(positions) < self.config['num_players']:
            pos = grid.get_random_position()
            if pos not in positions:
                positions.append(pos)
        
        for i in range(self.config['num_players']):
            name = CHARACTER_NAMES['6-8'][i]
            color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
            player = Player(i, name, color, positions[i])
            players.append(player)
        
        # Run the simulation
        engine = GameEngine(grid, players, protocol)
        engine.start_game()
        
        step_count = 0
        max_steps = 10000  # Safety limit
        
        while engine.game_active and step_count < max_steps:
            engine.step()
            step_count += 1
        
        # Collect results
        stats = engine.get_summary_statistics()
        
        return {
            'grid_size': grid_size,
            'protocol': protocol.value,
            'num_players': self.config['num_players'],
            'total_moves': stats.get('average_moves', 0),
            'step_count': step_count,
            'completed': not engine.game_active
        }
    
    def draw_progress(self):
        """Draw experiment progress."""
        self.screen.fill(COLORS['WHITE'])
        
        # Title
        title = self.font_medium.render("Running Experiments...", True, COLORS['BLACK'])
        self.screen.blit(title, (200, 200))
        
        # Progress bar
        progress_rect = pygame.Rect(200, 250, 400, 30)
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], progress_rect)
        
        if self.total_experiments > 0:
            progress_width = int((self.current_progress / self.total_experiments) * 400)
            filled_rect = pygame.Rect(200, 250, progress_width, 30)
            pygame.draw.rect(self.screen, COLORS['GREEN'], filled_rect)
        
        pygame.draw.rect(self.screen, COLORS['BLACK'], progress_rect, 2)
        
        # Progress text
        progress_text = f"{self.current_progress} / {self.total_experiments}"
        text = self.font_small.render(progress_text, True, COLORS['BLACK'])
        text_rect = text.get_rect(center=(400, 265))
        self.screen.blit(text, text_rect)
        
        # Current experiment info
        if self.current_progress < self.total_experiments and self.results:
            current_info = "Running experiments..."
        elif self.completed:
            current_info = "Experiments completed!"
        else:
            current_info = "Preparing experiments..."
        
        info_text = self.font_small.render(current_info, True, COLORS['BLACK'])
        self.screen.blit(info_text, (200, 300))


class DataAnalyzer:
    """Analyzes experiment results and creates visualizations."""
    
    def __init__(self, results: List[Dict[str, Any]]):
        self.results = results
        
    def analyze_by_grid_size(self) -> Dict[str, Any]:
        """Analyze results by grid size."""
        size_data = {}
        
        for result in self.results:
            size_key = f"{result['grid_size'][0]}×{result['grid_size'][1]}"
            
            if size_key not in size_data:
                size_data[size_key] = []
            
            size_data[size_key].append(result['total_moves'])
        
        # Calculate statistics
        analysis = {}
        for size, moves_list in size_data.items():
            analysis[size] = {
                'mean': np.mean(moves_list),
                'std': np.std(moves_list),
                'min': np.min(moves_list),
                'max': np.max(moves_list),
                'count': len(moves_list)
            }
        
        return analysis
    
    def analyze_by_protocol(self) -> Dict[str, Any]:
        """Analyze results by movement protocol."""
        protocol_data = {}
        
        for result in self.results:
            protocol = result['protocol']
            
            if protocol not in protocol_data:
                protocol_data[protocol] = []
            
            protocol_data[protocol].append(result['total_moves'])
        
        # Calculate statistics
        analysis = {}
        for protocol, moves_list in protocol_data.items():
            analysis[protocol] = {
                'mean': np.mean(moves_list),
                'std': np.std(moves_list),
                'min': np.min(moves_list),
                'max': np.max(moves_list),
                'count': len(moves_list)
            }
        
        return analysis
    
    def create_comparison_chart(self, analysis_type: str = 'grid_size') -> pygame.Surface:
        """Create a comparison chart as a pygame surface."""
        if analysis_type == 'grid_size':
            data = self.analyze_by_grid_size()
            title = 'Average Moves by Grid Size'
            xlabel = 'Grid Size'
        else:
            data = self.analyze_by_protocol()
            title = 'Average Moves by Movement Protocol'
            xlabel = 'Protocol'
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = list(data.keys())
        means = [data[cat]['mean'] for cat in categories]
        stds = [data[cat]['std'] for cat in categories]
        
        bars = ax.bar(categories, means, yerr=stds, capsize=5, 
                     color='skyblue', edgecolor='navy', alpha=0.7)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Average Number of Moves', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(stds)*0.1,
                   f'{mean:.1f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Convert to pygame surface
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=80, bbox_inches='tight')
        buf.seek(0)
        
        # Load as pygame surface
        import pygame.image
        chart_surface = pygame.image.load(buf)
        
        plt.close(fig)
        buf.close()
        
        return chart_surface


class Grades68GameRenderer:
    """Handles rendering for the 6-8 grade version with advanced UI."""
    
    def __init__(self, screen: pygame.Surface, grid: Grid):
        self.screen = screen
        self.grid = grid
        self.cell_size = min(CELL_SIZE, 600 // max(grid.width, grid.height))
        
        # Calculate grid position
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        self.grid_x = 50
        self.grid_y = 100
        
        # Fonts
        pygame.font.init()
        self.large_font = pygame.font.Font(None, 32)
        self.medium_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def draw_advanced_grid(self, players: List[Player], protocol: MovementProtocol):
        """Draw grid with advanced visualization features."""
        # Grid background
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_x = self.grid_x + x * self.cell_size
                cell_y = self.grid_y + y * self.cell_size
                
                # Color based on grid pattern
                if (x + y) % 2 == 0:
                    color = COLORS['LIGHT_GREEN']
                else:
                    color = COLORS['GREEN']
                
                pygame.draw.rect(self.screen, color, 
                               (cell_x, cell_y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, COLORS['DARK_GREEN'], 
                               (cell_x, cell_y, self.cell_size, self.cell_size), 1)
        
        # Draw movement traces if space allows
        if self.cell_size >= 20:
            self._draw_movement_traces(players)
        
        # Draw players
        self._draw_advanced_players(players)
        
        # Draw protocol indicator
        self._draw_protocol_indicator(protocol)
    
    def _draw_movement_traces(self, players: List[Player]):
        """Draw traces of recent player movements."""
        # This would show the last few positions of each player
        # For simplicity, we'll skip this in this implementation
        pass
    
    def _draw_advanced_players(self, players: List[Player]):
        """Draw players with enhanced visualization."""
        for player in players:
            cell_x = self.grid_x + player.position.x * self.cell_size
            cell_y = self.grid_y + player.position.y * self.cell_size
            
            center_x = cell_x + self.cell_size // 2
            center_y = cell_y + self.cell_size // 2
            
            # Player color
            color = PLAYER_COLORS[player.id % len(PLAYER_COLORS)]
            
            # Draw player
            radius = max(8, self.cell_size // 4)
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
            pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x, center_y), radius, 2)
            
            # Draw player ID
            if self.cell_size >= 20:
                text = self.small_font.render(str(player.id + 1), True, COLORS['WHITE'])
                text_rect = text.get_rect(center=(center_x, center_y))
                self.screen.blit(text, text_rect)
            
            # Draw "found" indicator
            if player.is_found:
                pygame.draw.circle(self.screen, COLORS['YELLOW'], 
                                 (center_x, center_y), radius + 3, 3)
    
    def _draw_protocol_indicator(self, protocol: MovementProtocol):
        """Draw current movement protocol indicator."""
        protocol_text = f"Protocol: {protocol.value.replace('_', ' ').title()}"
        text = self.medium_font.render(protocol_text, True, COLORS['BLACK'])
        self.screen.blit(text, (self.grid_x, self.grid_y - 30))
    
    def draw_experiment_results_panel(self, analyzer: Optional[DataAnalyzer]):
        """Draw experiment results panel."""
        panel_x = self.grid_x + self.grid.width * self.cell_size + 20
        panel_y = self.grid_y
        panel_width = 300
        
        # Panel background
        pygame.draw.rect(self.screen, COLORS['WHITE'], 
                        (panel_x, panel_y, panel_width, 400))
        pygame.draw.rect(self.screen, COLORS['BLACK'], 
                        (panel_x, panel_y, panel_width, 400), 2)
        
        # Title
        title = self.medium_font.render("Data Analysis", True, COLORS['BLACK'])
        self.screen.blit(title, (panel_x + 10, panel_y + 10))
        
        if analyzer:
            # Show summary statistics
            grid_analysis = analyzer.analyze_by_grid_size()
            protocol_analysis = analyzer.analyze_by_protocol()
            
            y_offset = 50
            
            # Grid size analysis
            section_title = self.small_font.render("By Grid Size:", True, COLORS['BLACK'])
            self.screen.blit(section_title, (panel_x + 10, panel_y + y_offset))
            y_offset += 25
            
            for size, stats in list(grid_analysis.items())[:3]:  # Show top 3
                stat_text = f"{size}: {stats['mean']:.1f} ± {stats['std']:.1f}"
                text = pygame.font.Font(None, 16).render(stat_text, True, COLORS['BLACK'])
                self.screen.blit(text, (panel_x + 20, panel_y + y_offset))
                y_offset += 20
            
            y_offset += 20
            
            # Protocol analysis
            section_title = self.small_font.render("By Protocol:", True, COLORS['BLACK'])
            self.screen.blit(section_title, (panel_x + 10, panel_y + y_offset))
            y_offset += 25
            
            for protocol, stats in protocol_analysis.items():
                protocol_name = protocol.replace('_', ' ').title()[:8] + "..."
                stat_text = f"{protocol_name}: {stats['mean']:.1f}"
                text = pygame.font.Font(None, 16).render(stat_text, True, COLORS['BLACK'])
                self.screen.blit(text, (panel_x + 20, panel_y + y_offset))
                y_offset += 20


class Grades68Game:
    """Main game class for grades 6-8 with advanced features."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        
        # Game state
        self.state = "menu"  # menu, experiment_design, running_experiment, analysis, manual_play
        
        # Components
        self.experiment_designer = None
        self.experiment_runner = None
        self.data_analyzer = None
        
        # Manual play components
        self.grid = None
        self.players = []
        self.engine = None
        self.renderer = None
        self.current_protocol = MovementProtocol.RANDOM
        
        # UI
        self.menu_buttons = self._create_menu_buttons()
        self.analysis_buttons = self._create_analysis_buttons()
        
        # Game timing for manual play
        self.auto_play = True
        self.move_timer = 0
        self.move_interval = 400
    
    def _create_menu_buttons(self) -> Dict[str, pygame.Rect]:
        """Create main menu buttons."""
        return {
            'run_experiment': pygame.Rect(200, 200, 200, 50),
            'manual_play': pygame.Rect(200, 270, 200, 50),
            'view_data': pygame.Rect(200, 340, 200, 50),
            'back': pygame.Rect(200, 410, 200, 50)
        }
    
    def _create_analysis_buttons(self) -> Dict[str, pygame.Rect]:
        """Create analysis view buttons."""
        return {
            'grid_size_chart': pygame.Rect(50, 500, 150, 40),
            'protocol_chart': pygame.Rect(220, 500, 150, 40),
            'export_data': pygame.Rect(390, 500, 120, 40),
            'back_to_menu': pygame.Rect(530, 500, 100, 40)
        }
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events based on current state."""
        if self.state == "menu":
            return self._handle_menu_events(event)
        elif self.state == "experiment_design":
            return self._handle_experiment_design_events(event)
        elif self.state == "running_experiment":
            return self._handle_experiment_running_events(event)
        elif self.state == "analysis":
            return self._handle_analysis_events(event)
        elif self.state == "manual_play":
            return self._handle_manual_play_events(event)
        
        return True
    
    def _handle_menu_events(self, event: pygame.event.Event) -> bool:
        """Handle main menu events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.menu_buttons['run_experiment'].collidepoint(mouse_pos):
                self.state = "experiment_design"
                self.experiment_designer = ExperimentDesigner(self.screen)
                return True
            elif self.menu_buttons['manual_play'].collidepoint(mouse_pos):
                self._start_manual_play()
                return True
            elif self.menu_buttons['view_data'].collidepoint(mouse_pos):
                if hasattr(self, 'last_experiment_results') and self.last_experiment_results:
                    self.state = "analysis"
                    self.data_analyzer = DataAnalyzer(self.last_experiment_results)
                return True
            elif self.menu_buttons['back'].collidepoint(mouse_pos):
                return False  # Return to grade selection
        
        return True
    
    def _handle_experiment_design_events(self, event: pygame.event.Event) -> bool:
        """Handle experiment design events."""
        if self.experiment_designer:
            self.experiment_designer.handle_event(event)
            
            if self.experiment_designer.experiment_ready:
                config = self.experiment_designer.get_experiment_config()
                self.state = "running_experiment"
                self.experiment_runner = ExperimentRunner(config, self.screen)
                # Start running experiments in next update cycle
                return True
            elif self.experiment_designer.cancelled:
                self.state = "menu"
                return True
        
        return True
    
    def _handle_experiment_running_events(self, event: pygame.event.Event) -> bool:
        """Handle events during experiment running."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "menu"
                return True
        
        return True
    
    def _handle_analysis_events(self, event: pygame.event.Event) -> bool:
        """Handle analysis view events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.analysis_buttons['back_to_menu'].collidepoint(mouse_pos):
                self.state = "menu"
                return True
            # Add chart switching and data export functionality here
        
        return True
    
    def _handle_manual_play_events(self, event: pygame.event.Event) -> bool:
        """Handle manual play events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Add manual play controls here
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "menu"
                return True
            elif event.key == pygame.K_SPACE:
                self.auto_play = not self.auto_play
                return True
            elif event.key == pygame.K_p:
                # Cycle through protocols
                protocols = list(MovementProtocol)
                current_index = protocols.index(self.current_protocol)
                self.current_protocol = protocols[(current_index + 1) % len(protocols)]
                if self.engine:
                    self.engine.movement_protocol = self.current_protocol
                return True
        
        return True
    
    def _start_manual_play(self):
        """Start manual play mode."""
        self.state = "manual_play"
        
        # Create a default 7x7 grid with 2 players
        self.grid = Grid(7, 7)
        
        # Create players
        self.players = []
        positions = [Position(0, 0), Position(6, 6)]  # Opposite corners
        
        for i in range(2):
            name = CHARACTER_NAMES['6-8'][i]
            color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
            player = Player(i, name, color, positions[i])
            self.players.append(player)
        
        # Create engine and renderer
        self.engine = GameEngine(self.grid, self.players, self.current_protocol)
        self.renderer = Grades68GameRenderer(self.screen, self.grid)
        
        # Start the game
        self.engine.start_game()
    
    def update(self, dt: int):
        """Update the current state."""
        if self.state == "running_experiment" and self.experiment_runner:
            if not self.experiment_runner.running and not self.experiment_runner.completed:
                # Start the experiment
                self.experiment_runner.run_experiments()
            elif self.experiment_runner.completed:
                # Experiment finished, show results
                self.last_experiment_results = self.experiment_runner.results
                self.state = "analysis"
                self.data_analyzer = DataAnalyzer(self.last_experiment_results)
        
        elif self.state == "manual_play" and self.engine and self.auto_play:
            self.move_timer += dt
            
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                
                continue_game = self.engine.step()
                
                if not continue_game:
                    # Game ended, restart automatically
                    self._start_manual_play()
    
    def draw(self):
        """Draw the current state."""
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "experiment_design":
            if self.experiment_designer:
                self.experiment_designer.draw()
        elif self.state == "running_experiment":
            if self.experiment_runner:
                self.experiment_runner.draw_progress()
        elif self.state == "analysis":
            self._draw_analysis()
        elif self.state == "manual_play":
            self._draw_manual_play()
    
    def _draw_menu(self):
        """Draw the main menu."""
        self.screen.fill(COLORS['LIGHT_BLUE'])
        
        # Title
        title = pygame.font.Font(None, 48).render("Advanced Grid Analysis Lab", True, COLORS['BLACK'])
        title_rect = title.get_rect(center=(self.screen.get_width()//2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = pygame.font.Font(None, 24).render("Grades 6-8: Computational Thinking & Data Science", True, COLORS['BLACK'])
        subtitle_rect = subtitle.get_rect(center=(self.screen.get_width()//2, 140))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu buttons
        button_configs = {
            'run_experiment': ("Design & Run Experiment", COLORS['GREEN']),
            'manual_play': ("Manual Exploration", COLORS['BLUE']),
            'view_data': ("Analyze Previous Data", COLORS['ORANGE']),
            'back': ("Back to Grade Selection", COLORS['RED'])
        }
        
        font = pygame.font.Font(None, 24)
        
        for button_name, (text, color) in button_configs.items():
            button_rect = self.menu_buttons[button_name]
            
            # Enable/disable view data button
            if button_name == 'view_data':
                if not hasattr(self, 'last_experiment_results') or not self.last_experiment_results:
                    color = COLORS['GRAY']
            
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, COLORS['BLACK'], button_rect, 2)
            
            text_surface = font.render(text, True, COLORS['BLACK'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_analysis(self):
        """Draw the analysis view."""
        self.screen.fill(COLORS['WHITE'])
        
        if self.data_analyzer:
            # Draw analysis results
            title = pygame.font.Font(None, 32).render("Experiment Results Analysis", True, COLORS['BLACK'])
            self.screen.blit(title, (50, 20))
            
            # Show summary statistics
            grid_analysis = self.data_analyzer.analyze_by_grid_size()
            protocol_analysis = self.data_analyzer.analyze_by_protocol()
            
            y_offset = 80
            
            # Grid size results
            section_title = pygame.font.Font(None, 24).render("Results by Grid Size:", True, COLORS['BLACK'])
            self.screen.blit(section_title, (50, y_offset))
            y_offset += 30
            
            for size, stats in grid_analysis.items():
                result_text = f"{size}: Average {stats['mean']:.1f} moves (±{stats['std']:.1f})"
                text = pygame.font.Font(None, 18).render(result_text, True, COLORS['BLACK'])
                self.screen.blit(text, (70, y_offset))
                y_offset += 25
            
            y_offset += 20
            
            # Protocol results
            section_title = pygame.font.Font(None, 24).render("Results by Protocol:", True, COLORS['BLACK'])
            self.screen.blit(section_title, (50, y_offset))
            y_offset += 30
            
            for protocol, stats in protocol_analysis.items():
                protocol_name = protocol.replace('_', ' ').title()
                result_text = f"{protocol_name}: Average {stats['mean']:.1f} moves (±{stats['std']:.1f})"
                text = pygame.font.Font(None, 18).render(result_text, True, COLORS['BLACK'])
                self.screen.blit(text, (70, y_offset))
                y_offset += 25
        
        # Draw analysis buttons
        button_configs = {
            'grid_size_chart': ("Grid Chart", COLORS['GREEN']),
            'protocol_chart': ("Protocol Chart", COLORS['BLUE']),
            'export_data': ("Export Data", COLORS['ORANGE']),
            'back_to_menu': ("Back", COLORS['RED'])
        }
        
        font = pygame.font.Font(None, 20)
        
        for button_name, (text, color) in button_configs.items():
            button_rect = self.analysis_buttons[button_name]
            
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, COLORS['BLACK'], button_rect, 2)
            
            text_surface = font.render(text, True, COLORS['BLACK'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_manual_play(self):
        """Draw the manual play interface."""
        self.screen.fill(COLORS['LIGHT_GRAY'])
        
        if self.renderer and self.engine:
            # Draw the game
            self.renderer.draw_advanced_grid(self.players, self.current_protocol)
            
            # Draw game info panel
            self._draw_manual_play_info()
    
    def _draw_manual_play_info(self):
        """Draw information panel for manual play."""
        panel_x = 50
        panel_y = 20
        panel_width = 600
        panel_height = 70
        
        # Panel background
        pygame.draw.rect(self.screen, COLORS['WHITE'], 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, COLORS['BLACK'], 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Game status
        if self.engine.game_active:
            total_moves = sum(p.move_count for p in self.players)
            status_text = f"Active - Total Moves: {total_moves}"
        else:
            status_text = "Game Complete - Restarting..."
        
        status = pygame.font.Font(None, 24).render(status_text, True, COLORS['BLACK'])
        self.screen.blit(status, (panel_x + 10, panel_y + 10))
        
        # Protocol info
        protocol_text = f"Protocol: {self.current_protocol.value.replace('_', ' ').title()}"
        protocol_surface = pygame.font.Font(None, 20).render(protocol_text, True, COLORS['BLACK'])
        self.screen.blit(protocol_surface, (panel_x + 10, panel_y + 35))
        
        # Controls
        controls_text = "Controls: SPACE=Pause/Play, P=Change Protocol, ESC=Menu"
        controls_surface = pygame.font.Font(None, 16).render(controls_text, True, COLORS['BLACK'])
        self.screen.blit(controls_surface, (panel_x + 10, panel_y + 55))