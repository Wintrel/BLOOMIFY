import pygame
import sys
from settings import *
from state_manager import StateManager
import settings_manager
from ui.settings_menu import SettingsMenu


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # --- Load and Apply Settings ---
        settings_manager.load_settings()

        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("BLOOMIFY")
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = True

        self.state_manager = StateManager()
        self.settings_menu = SettingsMenu()  # Create the settings overlay

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS)
            self.get_events()
            self.update()
            self.draw()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # --- Hotkey for Settings Menu ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o and (event.mod & pygame.KMOD_CTRL):
                    self.settings_menu.toggle()

            # Pass events to the settings menu if active or animating
            if self.settings_menu.is_active or self.settings_menu.is_animating:
                self.settings_menu.get_event(event)
            else:
                self.state_manager.get_event(event)

    def update(self):
        # Update the settings menu if active or animating
        if self.settings_menu.is_active or self.settings_menu.is_animating:
            self.settings_menu.update(self.dt)
        else:
            self.state_manager.update(self.dt)

        # Check for state completion
        if self.state_manager.is_done():
            self.running = False

    def draw(self):
        # Always draw the state first
        self.state_manager.draw(self.screen)

        # Draw the settings menu on top if active or animating
        self.settings_menu.draw(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
