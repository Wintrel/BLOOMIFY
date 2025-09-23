import os

import pygame
from .base import BaseState
from settings import *
from .utility import draw_text

class LoadingScreen(BaseState):
    def __init__(self):
        super(LoadingScreen, self).__init__()
        self.next_state = "GAMEPLAY"
        self.time_active = 0
        self.song_data = {}

    def startup(self, persistent):
        super().startup(persistent)
        self.song_data = self.persist.get("selected_song_data", {})
        self.time_active = 0

        # Load the music file from the path provided by song_select
        audio_path = self.song_data.get("audio_path")
        if audio_path and os.path.exists(audio_path):
            try:
                pygame.mixer.music.load(audio_path)
                print(f"Successfully loaded music: {audio_path}")
            except pygame.error as e:
                print(f"Error loading music file {audio_path}: {e}")
        else:
            print("No audio path found for the selected song.")

    def update(self, dt):
        super().update(dt) # This is crucial to update the transition timers
        self.time_active += dt

        # --- FIX: Only trigger the transition out ONCE ---
        # We check if the state is 'static' (not already transitioning)
        if self.transition_state == "static" and self.time_active >= 1500: # 1.5 seconds
            self.go_to_next_state()

    def draw(self, surface):
        background = self.persist.get("selected_song_data", {}).get("final_background")
        if background:
            surface.blit(background, (0, 0))
        else:
            surface.fill(BLACK)

        # Use the transition alpha from the base state for a smooth fade
        draw_text(surface, "LOADING...", self.screen_rect.center, self.font, WHITE,
                  text_rect_origin='center', alpha=self.get_transition_alpha())

