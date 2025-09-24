import pygame
from settings import *
from states.base_state import BaseState
from ui.ui_manager import UIManager

class MainMenuState(BaseState):
    def __init__(self, state_manager):
        super(MainMenuState, self).__init__(state_manager)
        self.next_state = "SONG_SELECT"
        
        self.ui_manager = UIManager()
        self.ui_manager.load_layout("layouts/Main_Menu_Layout.json")

        self.is_transitioning_out = False
        self.transition_anim_duration = 0.5 # seconds

    def get_event(self, event):
        super().get_event(event)
        if not self.is_transitioning_out and self.transition_state == "static":
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                self.trigger_transition_out()

    def trigger_transition_out(self):
        """ Kicks off the slide-out animations for all UI elements. """
        self.is_transitioning_out = True
        # --- FIX: This is the crucial missing signal ---
        # This tells the base state to start its own fade-out timer.
        self.go_to_next_state() 
        
        # Animate title up and off-screen
        title = self.ui_manager.get_element_by_name("game_name")
        if title:
            target_y = -title.size[1]
            title.animate_position((title.absolute_pos[0], target_y), self.transition_anim_duration)
            
        # Animate subtitle down and off-screen
        subtitle = self.ui_manager.get_element_by_name("game_desc")
        if subtitle:
            target_y = self.screen_rect.height
            subtitle.animate_position((subtitle.absolute_pos[0], target_y), self.transition_anim_duration)
            
        # Animate prompt down and off-screen
        prompt = self.ui_manager.get_element_by_name("click_prompt")
        if prompt:
            target_y = self.screen_rect.height
            prompt.animate_position((prompt.absolute_pos[0], target_y), self.transition_anim_duration)
            
    def update(self, dt):
        super().update(dt)
        self.ui_manager.update(dt)
        # The base_state's update now correctly handles setting self.done = True

    def draw(self, surface):
        surface.fill(BLACK)
        self.ui_manager.draw(surface)

