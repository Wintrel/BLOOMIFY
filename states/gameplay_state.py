import pygame
import os
from settings import *
from states.base_state import BaseState
from gameplay.context import GameContext
from gameplay.note_manager import NoteManager
from gameplay.lane_manager import LaneManager
from gameplay.mechanics_manager import MechanicManager
from gameplay.hud_manager import HUDManager
from ui.ui_manager import UIManager
from ui.button import Button
import asset_loader


class GameplayState(BaseState):
    def __init__(self, state_manager):
        super(GameplayState, self).__init__(state_manager)
        self.next_state = "RESULTS"

        self.is_paused = False
        self.pause_ui = UIManager()
        self.pause_ui.load_layout("layouts/pause_menu.json")
        self.setup_pause_buttons()

        self.gameplay_surface = pygame.Surface(SCREEN_SIZE)
        self.zoom_level = 1.0
        self.target_zoom = 1.0

    def startup(self, persistent):
        super().startup(persistent)
        # --- Reset pause state on startup ---
        self.is_paused = False
        self.zoom_level = 1.0
        self.target_zoom = 1.0

        song_data = self.persist.get("selected_song_data", {})
        chart = self.persist.get("chart")
        if not chart:
            self.next_state = "SONG_SELECT"
            self.go_to_next_state()
            return
        self.next_state = "RESULTS"
        self.context = GameContext(chart, self.screen_rect)
        self.lane_manager = LaneManager(self.context)
        self.note_manager = NoteManager(self.context)
        self.mechanic_manager = MechanicManager(self.context)
        self.hud_manager = HUDManager(self.context)
        original_img = asset_loader.load_image(song_data.get("image_path"))
        if original_img:
            self.background_img = asset_loader.create_blurred_background(original_img, self.screen_rect.size)
        else:
            self.background_img = pygame.Surface(self.screen_rect.size);
            self.background_img.fill(BLACK)
        audio_path = song_data.get("audio_path")
        if audio_path and os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play(start=self.context.start_time_offset)

    def setup_pause_buttons(self):
        continue_btn = self.pause_ui.get_element_by_name("continue_button")
        if continue_btn: continue_btn.on_click = self.toggle_pause

        restart_btn = self.pause_ui.get_element_by_name("restart_button")
        if restart_btn: restart_btn.on_click = self.restart_song

        quit_btn = self.pause_ui.get_element_by_name("quit_button")
        if quit_btn: quit_btn.on_click = self.quit_to_menu

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.target_zoom = 0.8
            pygame.mixer.music.pause()
        else:
            self.target_zoom = 1.0
            pygame.mixer.music.unpause()

    def restart_song(self):
        self.next_state = "LOADING"
        self.go_to_next_state()

    def quit_to_menu(self):
        pygame.mixer.music.stop()  # Stop music when quitting to menu
        self.next_state = "SONG_SELECT"
        self.go_to_next_state()

    def get_event(self, event):
        super().get_event(event)

        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.toggle_pause()
            return

        if self.is_paused:
            self.pause_ui.get_event(event)
        elif self.transition_state == "static":
            self.note_manager.get_event(event)
            self.mechanic_manager.get_event(event)

    def update(self, dt):
        super().update(dt)

        zoom_speed = 5.0
        self.zoom_level += (self.target_zoom - self.zoom_level) * zoom_speed * (dt / 1000.0)

        if self.is_paused:
            self.pause_ui.update(dt)
        elif self.transition_state == "static":
            self.context.update_time(dt / 1000.0)
            self.lane_manager.update(dt)
            self.note_manager.update(dt)
            self.mechanic_manager.update(dt)

            if not self.note_manager.notes_to_spawn and not self.note_manager.active_notes:
                if self.transition_state == "static":
                    self.persist["results_data"] = self.context.get_results()
                    self.persist["selected_song_data"] = self.persist.get("selected_song_data")
                    pygame.mixer.music.fadeout(1000)
                    self.go_to_next_state()

    def draw_gameplay(self, surface):
        surface.blit(self.background_img, (0, 0))
        self.lane_manager.draw(surface)
        self.note_manager.draw(surface)
        self.mechanic_manager.draw(surface)
        self.hud_manager.draw(surface)

    def draw(self, surface):
        self.draw_gameplay(self.gameplay_surface)

        if abs(self.zoom_level - 1.0) < 0.001:
            surface.blit(self.gameplay_surface, (0, 0))
        else:
            scaled_size = (int(SCREEN_WIDTH * self.zoom_level), int(SCREEN_HEIGHT * self.zoom_level))
            scaled_surface = pygame.transform.smoothscale(self.gameplay_surface, scaled_size)

            surface.fill(BLACK)

            pos_x = (SCREEN_WIDTH - scaled_size[0]) / 2
            pos_y = (SCREEN_HEIGHT - scaled_size[1]) / 2
            surface.blit(scaled_surface, (pos_x, pos_y))

        if self.is_paused:
            overlay = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
            overlay_alpha = int(200 * (1 - ((self.zoom_level - 0.8) / 0.2)))
            overlay.fill((0, 0, 0, max(0, overlay_alpha)))  # Clamp alpha to be non-negative
            surface.blit(overlay, (0, 0))

            self.pause_ui.draw(surface)

