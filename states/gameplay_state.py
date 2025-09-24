import pygame
import os
from settings import *
from states.base_state import BaseState
from gameplay.context import GameContext
from gameplay.note_manager import NoteManager
from gameplay.lane_manager import LaneManager
from gameplay.mechanics_manager import MechanicManager
from gameplay.hud_manager import HUDManager
import asset_loader


class GameplayState(BaseState):
    def __init__(self, state_manager):
        super(GameplayState, self).__init__(state_manager)
        # --- FIX: Ensure the next state is always RESULTS ---
        self.next_state = "RESULTS"

    def startup(self, persistent):
        super().startup(persistent)
        song_data = self.persist.get("selected_song_data", {})
        chart = self.persist.get("chart")

        if not chart:
            print("ERROR: No chart loaded into gameplay state! Returning to song select.")
            self.next_state = "SONG_SELECT"
            self.go_to_next_state()
            return

        # Reset next_state to RESULTS in case it was changed by an error
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
            self.background_img = pygame.Surface(self.screen_rect.size).fill(BLACK)

        audio_path = song_data.get("audio_path")
        if audio_path and os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play(start=self.context.start_time_offset)

    def get_event(self, event):
        super().get_event(event)
        if self.transition_state == "static":
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                self.next_state = "SONG_SELECT"
                self.go_to_next_state()
                return

            self.note_manager.get_event(event)
            self.mechanic_manager.get_event(event)

    def update(self, dt):
        super().update(dt)
        if self.transition_state != "static": return

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

    def draw(self, surface):
        surface.blit(self.background_img, (0, 0))
        self.lane_manager.draw(surface)
        self.note_manager.draw(surface)
        self.mechanic_manager.draw(surface)
        self.hud_manager.draw(surface)

