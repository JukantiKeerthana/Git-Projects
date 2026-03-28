"""
Audio management system for the Wandering in the Woods game.
Handles background music, sound effects, and text-to-speech announcements.
"""

import pygame
import os
from typing import Dict, Optional
import threading
import platform

# Try to import text-to-speech capability
TTS_AVAILABLE = False
try:
    if platform.system() == "Darwin":  # macOS
        import subprocess
        TTS_AVAILABLE = True
    elif platform.system() == "Windows":
        import pyttsx3
        TTS_AVAILABLE = True
    else:  # Linux and others
        try:
            import subprocess
            # Test if espeak is available
            subprocess.run(['which', 'espeak'], check=True, capture_output=True)
            TTS_AVAILABLE = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
except ImportError:
    pass


class AudioManager:
    """Manages all audio for the game including music, sound effects, and TTS."""
    
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.music_volume = 0.5
        self.sfx_volume = 0.8
        self.tts_enabled = True
        
        # Audio dictionaries
        self.music_tracks: Dict[str, str] = {}
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        
        # TTS setup
        self.tts_engine = None
        if TTS_AVAILABLE:
            self._setup_tts()
        
        # Load built-in sounds (we'll create simple ones programmatically)
        self._create_default_sounds()
    
    def _setup_tts(self):
        """Setup text-to-speech engine based on platform."""
        try:
            if platform.system() == "Windows":
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)  # Slower rate for kids
                self.tts_engine.setProperty('volume', 0.8)
            # For macOS and Linux, we'll use system commands
        except Exception as e:
            print(f"TTS setup failed: {e}")
            self.tts_enabled = False
    
    def _create_default_sounds(self):
        """Create simple sound effects programmatically."""
        # Create celebration sound (ascending notes)
        self.sound_effects['celebration'] = self._create_tone_sequence([
            (523, 200),  # C5
            (659, 200),  # E5
            (784, 200),  # G5
            (1047, 400)  # C6
        ])
        
        # Create step sound (short click)
        self.sound_effects['step'] = self._create_tone(800, 50)
        
        # Create meeting sound (pleasant chime)
        self.sound_effects['meeting'] = self._create_tone_sequence([
            (659, 150),  # E5
            (784, 150),  # G5
            (1047, 300)  # C6
        ])
        
        # Create button click sound
        self.sound_effects['click'] = self._create_tone(440, 100)
        
        # Create reset sound
        self.sound_effects['reset'] = self._create_tone(330, 150)
    
    def _create_tone(self, frequency: int, duration_ms: int) -> pygame.mixer.Sound:
        """Create a simple tone sound effect."""
        sample_rate = 22050
        frames = int(duration_ms * sample_rate / 1000)
        
        import numpy as np
        
        # Generate sine wave
        arr = np.zeros((frames, 2), dtype=np.int16)
        for i in range(frames):
            time_val = float(i) / sample_rate
            wave = int(4096 * np.sin(frequency * 2 * np.pi * time_val))
            
            # Apply fade in/out to avoid clicks
            fade_frames = min(frames // 10, 500)
            if i < fade_frames:
                wave = int(wave * i / fade_frames)
            elif i > frames - fade_frames:
                wave = int(wave * (frames - i) / fade_frames)
            
            arr[i][0] = wave  # Left channel
            arr[i][1] = wave  # Right channel
        
        return pygame.sndarray.make_sound(arr)
    
    def _create_tone_sequence(self, notes: list) -> pygame.mixer.Sound:
        """Create a sequence of tones."""
        import numpy as np
        
        sample_rate = 22050
        total_duration = sum(duration for _, duration in notes)
        total_frames = int(total_duration * sample_rate / 1000)
        
        arr = np.zeros((total_frames, 2), dtype=np.int16)
        
        current_frame = 0
        for frequency, duration_ms in notes:
            frames = int(duration_ms * sample_rate / 1000)
            
            for i in range(frames):
                if current_frame + i >= total_frames:
                    break
                
                time_val = float(i) / sample_rate
                wave = int(4096 * np.sin(frequency * 2 * np.pi * time_val))
                
                # Apply fade in/out
                fade_frames = min(frames // 10, 200)
                if i < fade_frames:
                    wave = int(wave * i / fade_frames)
                elif i > frames - fade_frames:
                    wave = int(wave * (frames - i) / fade_frames)
                
                arr[current_frame + i][0] = wave
                arr[current_frame + i][1] = wave
            
            current_frame += frames
        
        return pygame.sndarray.make_sound(arr)
    
    def load_music(self, name: str, file_path: str):
        """Load a music track."""
        if os.path.exists(file_path):
            self.music_tracks[name] = file_path
        else:
            print(f"Music file not found: {file_path}")
    
    def load_sound_effect(self, name: str, file_path: str):
        """Load a sound effect."""
        if os.path.exists(file_path):
            try:
                self.sound_effects[name] = pygame.mixer.Sound(file_path)
            except pygame.error as e:
                print(f"Could not load sound {file_path}: {e}")
        else:
            print(f"Sound file not found: {file_path}")
    
    def play_music(self, name: str, loops: int = -1, fade_ms: int = 0):
        """Play background music."""
        if name in self.music_tracks:
            try:
                pygame.mixer.music.load(self.music_tracks[name])
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
            except pygame.error as e:
                print(f"Could not play music {name}: {e}")
    
    def stop_music(self, fade_ms: int = 1000):
        """Stop background music."""
        pygame.mixer.music.fadeout(fade_ms)
    
    def play_sound(self, name: str):
        """Play a sound effect."""
        if name in self.sound_effects:
            sound = self.sound_effects[name]
            sound.set_volume(self.sfx_volume)
            sound.play()
    
    def speak_text(self, text: str, priority: bool = False):
        """Speak text using text-to-speech (runs in background thread)."""
        if not self.tts_enabled or not TTS_AVAILABLE:
            print(f"TTS: {text}")  # Fallback to console output
            return
        
        # Run TTS in a separate thread to avoid blocking the game
        def tts_thread():
            try:
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(['say', text], check=True)
                elif platform.system() == "Windows" and self.tts_engine:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                else:  # Linux with espeak
                    subprocess.run(['espeak', text], check=True)
            except Exception as e:
                print(f"TTS error: {e}")
        
        if priority:
            # For important announcements, run immediately
            threading.Thread(target=tts_thread, daemon=True).start()
        else:
            # For less important announcements, add slight delay
            def delayed_tts():
                import time
                time.sleep(0.5)
                tts_thread()
            
            threading.Thread(target=delayed_tts, daemon=True).start()
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_tts_enabled(self, enabled: bool):
        """Enable or disable text-to-speech."""
        self.tts_enabled = enabled and TTS_AVAILABLE
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing."""
        return pygame.mixer.music.get_busy()
    
    def cleanup(self):
        """Clean up audio resources."""
        pygame.mixer.music.stop()
        pygame.mixer.quit()


# K-2 specific audio prompts
K2_AUDIO_PROMPTS = {
    'welcome': "Welcome to the Wandering Woods! Help Bunny and Bear find each other!",
    'game_start': "The adventure begins! Bunny and Bear are looking for each other.",
    'game_end': "Hooray! They found each other! Great job!",
    'moves_announcement': "Let's see how many steps it took!",
    'reset': "Starting a new adventure in the woods!",
    'celebration': "Yay! What a wonderful meeting in the forest!"
}

# 3-5 specific audio prompts
GRADES35_AUDIO_PROMPTS = {
    'welcome': "Welcome explorers! Configure your grid and help your team find each other.",
    'game_start': "The exploration begins! Your team is searching through the grid.",
    'game_end': "Excellent! All team members have found each other!",
    'stats_summary': "Here are your exploration statistics.",
    'new_record': "Congratulations! That was your fastest time yet!",
    'player_found': "Great! Two explorers have met up and will now search together."
}

# 6-8 specific audio prompts  
GRADES68_AUDIO_PROMPTS = {
    'welcome': "Welcome to the Advanced Grid Exploration Lab!",
    'experiment_start': "Beginning data collection for your experiment.",
    'experiment_complete': "Experiment completed. Analyzing results...",
    'protocol_change': "Switching to a new exploration protocol.",
    'data_insight': "Interesting! Notice how the grid size affects the results.",
    'analysis_ready': "Your data analysis is ready for review."
}


class GradeSpecificAudio:
    """Handles grade-specific audio prompts and behaviors."""
    
    def __init__(self, audio_manager: AudioManager, grade_level: str):
        self.audio_manager = audio_manager
        self.grade_level = grade_level
        
        if grade_level == 'K2':
            self.prompts = K2_AUDIO_PROMPTS
        elif grade_level == '3-5':
            self.prompts = GRADES35_AUDIO_PROMPTS
        elif grade_level == '6-8':
            self.prompts = GRADES68_AUDIO_PROMPTS
        else:
            self.prompts = {}
    
    def announce_welcome(self):
        """Play welcome message for the grade level."""
        if 'welcome' in self.prompts:
            self.audio_manager.speak_text(self.prompts['welcome'], priority=True)
    
    def announce_game_start(self):
        """Announce game start."""
        if 'game_start' in self.prompts:
            self.audio_manager.speak_text(self.prompts['game_start'])
        self.audio_manager.play_sound('click')
    
    def announce_game_end(self, stats: dict = None):
        """Announce game completion with stats."""
        if 'game_end' in self.prompts:
            self.audio_manager.speak_text(self.prompts['game_end'])
        
        self.audio_manager.play_sound('celebration')
        
        # Grade-specific statistics announcements
        if stats and self.grade_level == 'K2':
            total_moves = stats.get('average_moves', 0)
            if total_moves > 0:
                moves_text = f"It took {int(total_moves)} steps to find each other!"
                self.audio_manager.speak_text(moves_text)
    
    def announce_reset(self):
        """Announce game reset."""
        if 'reset' in self.prompts:
            self.audio_manager.speak_text(self.prompts['reset'])
        self.audio_manager.play_sound('reset')