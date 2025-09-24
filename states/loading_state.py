import pygame
import os
from settings import *
from states.base_state import BaseState
from ui.ui_manager import UIManager
from ui.image_panel import ImagePanel
from ui.custom_widgets.Animated_arc_Widget import AnimatedArc
from gameplay import chart_loader
import asset_loader

class LoadingState(BaseState):
    def __init__(self, state_manager):
        super(LoadingState, self).__init__(state_manager)
        self.next_state = "GAMEPLAY"
        
        self.ui_manager = UIManager()
        self.ui_manager.load_layout("layouts/Loading_Layout.json")

        self.song_data = {}
        
        placeholder = self.ui_manager.get_element_by_name("loading_ellipse")
        if placeholder:
            self.loading_arc = AnimatedArc(pos=placeholder.absolute_pos, size=placeholder.size, width=10, color=(255,255,255), speed=-360)
        else: self.loading_arc = None

    def startup(self, persistent):
        super().startup(persistent)
        self.song_data = self.persist.get("selected_song_data", {})
        
        title = self.ui_manager.get_element_by_name("beatmaps_name")
        if title: title.set_text(self.song_data.get("title", "N/A"))
        
        artist = self.ui_manager.get_element_by_name("beatmapper_name")
        if artist: artist.set_text(self.song_data.get("artist", "N/A"))

        artwork_panel = self.ui_manager.get_element_by_name("IMG_beatmap_art_placeholder")
        if artwork_panel and isinstance(artwork_panel, ImagePanel):
            original_img = asset_loader.load_image(self.song_data.get("image_path"))
            artwork_panel.set_image(original_img)
            
        chart_path = self.song_data.get("beatmap_path")
        if chart_path:
            self.persist["chart"] = chart_loader.load_chart(chart_path)
        else: self.persist["chart"] = None
        
        audio_path = self.song_data.get("audio_path")
        if audio_path and os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            
        self.loading_timer = 2.0

    def update(self, dt):
        super().update(dt)
        if self.loading_arc: self.loading_arc.update(dt)
            
        self.loading_timer -= dt / 1000.0
        if self.loading_timer <= 0 and self.transition_state == "static":
            self.go_to_next_state()

    def draw(self, surface):
        surface.fill(BLACK)
        prev_state_bg = self.persist.get("final_background")
        if prev_state_bg:
            surface.blit(prev_state_bg, (0,0))

        # --- Create a temporary surface for the fade-in effect ---
        ui_surface = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
            
        self.ui_manager.draw(ui_surface)
        if self.loading_arc:
            self.loading_arc.draw(ui_surface)

        # Apply the master alpha from the base state and blit to the main screen
        ui_surface.set_alpha(self.get_transition_alpha())
        surface.blit(ui_surface, (0, 0))

