import pygame
from settings import *
from states.base_state import BaseState
from ui.ui_manager import UIManager
from ui.label import Label


class MainMenuState(BaseState):
    def __init__(self, state_manager):
        super(MainMenuState, self).__init__(state_manager)
        self.next_state = "SONG_SELECT"

        self.ui_manager = UIManager()
        self.ui_manager.load_layout("layouts/Main_Menu_Layout.json")

        # --- Find UI elements by name for animation ---
        self.subtitle_label = self.ui_manager.get_element_by_name("game_desc")
        self.click_prompt = self.ui_manager.get_element_by_name("click_prompt")

        # --- Animation state ---
        self.time_active = 0
        self.click_alpha = 0
        self.click_pulse_dir = 1
        self.animation_finished = False

    def update(self, dt):
        super().update(dt)
        self.ui_manager.update(dt)
        self.time_active += dt / 1000.0

        # Simple delay before showing the click prompt
        if not self.animation_finished and self.time_active > 1.5:
            self.animation_finished = True

        if self.animation_finished and self.click_prompt:
            # Pulsing alpha animation for the "click to bloom" text
            pulse_speed = 300
            self.click_alpha += self.click_pulse_dir * pulse_speed * (dt / 1000.0)
            if self.click_alpha >= 255:
                self.click_alpha = 255
                self.click_pulse_dir = -1
            elif self.click_alpha <= 50:
                self.click_alpha = 50
                self.click_pulse_dir = 1

            # This assumes your Label element can have its color's alpha changed
            # A more robust system would be to update the Label's color property directly.
            # For now, let's just make sure it exists before trying to access it.
            if hasattr(self.click_prompt, 'color'):
                original_color = self.click_prompt.color
                self.click_prompt.color = (original_color[0], original_color[1], original_color[2],
                                           int(self.click_alpha))
                self.click_prompt.create_text_surface()

    def get_event(self, event):
        super().get_event(event)
        if self.animation_finished:
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                if self.transition_state == "static":
                    self.go_to_next_state()

    def draw(self, surface):
        surface.fill(BLACK)
        self.ui_manager.draw(surface)

