import pygame
import math
from settings import *
from .base import BaseState
from .utility import draw_text, scale_to_cover


class LoadingScreen(BaseState):
    def __init__(self):
        super(LoadingScreen, self).__init__()
        self.next_state = "GAMEPLAY"
        self.time_active = 0
        self.selected_song = {}
        self.background_img = None
        self.banner_img = None

        # --- Fonts ---
        self.font_title = pygame.font.Font(None, 28)
        self.font_artist = pygame.font.Font(None, 18)

        # --- Transition ---
        # This state will have a fixed duration instead of an out-transition
        self.transition_duration = 0.4  # Fade in duration

    def startup(self, persistent):
        # We call super().startup AFTER getting the data, because we don't want
        # the default 'in' transition to start immediately.
        self.persist = persistent
        self.selected_song = self.persist.get("selected_song_data", {})

        self.background_img = self.selected_song.get("final_background")

        # Get banner image from song data
        unscaled_banner = self.selected_song.get("original_img")
        if unscaled_banner:
            self.banner_img = scale_to_cover(unscaled_banner, (400, 150))
        else:  # Fallback if no image
            self.banner_img = pygame.Surface((400, 150))
            self.banner_img.fill((30, 30, 30))

        # Reset and start the new transition in
        self.time_active = 0
        super().startup(persistent)

    def update(self, dt):
        super().update(dt)  # Handles the 'in' transition
        self.time_active += dt
        # After a 2-second loading period, this state is done.
        # The main game loop will then handle the state flip.
        if self.time_active >= 2000:
            self.done = True  # We don't need an 'out' transition here

    def draw(self, surface):
        if self.background_img:
            surface.blit(self.background_img, (0, 0))
        else:
            surface.fill(BLACK)

        # Create a UI surface to apply the master fade
        ui_surface = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)

        # --- Draw Banner and Text ---
        banner_rect = self.banner_img.get_rect(center=self.screen_rect.center)
        ui_surface.blit(self.banner_img, banner_rect)

        title_pos = (self.screen_rect.centerx, banner_rect.bottom + 30)
        draw_text(ui_surface, self.selected_song.get("title", "Loading..."), title_pos, self.font_title, WHITE,
                  text_rect_origin='center')

        artist_pos = (self.screen_rect.centerx, banner_rect.bottom + 55)
        draw_text(ui_surface, self.selected_song.get("artist", ""), artist_pos, self.font_artist, (200, 200, 200),
                  text_rect_origin='center')

        # --- Draw Loading Circle ---
        progress = (self.time_active % 1000) / 1000  # Loop animation every second

        # Start and end angles for the arc
        start_angle = -math.pi / 2  # 12 o'clock
        end_angle = start_angle + (progress * 2 * math.pi)

        circle_rect = pygame.Rect(0, 0, 100, 100)
        circle_rect.center = (self.screen_rect.centerx, banner_rect.top - 80)

        pygame.draw.arc(ui_surface, (255, 255, 255, 100), circle_rect, 0, 2 * math.pi, 6)  # Faint background circle
        pygame.draw.arc(ui_surface, WHITE, circle_rect, start_angle, end_angle, 6)

        # Apply master alpha and blit to the main surface
        ui_surface.set_alpha(self.transition_alpha)
        surface.blit(ui_surface, (0, 0))

