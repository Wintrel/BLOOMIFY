import pygame
import sys
from settings import *
from states.main_menu import MainMenu
from states.song_select import SongSelect
from states.loading import LoadingScreen
from states.gameplay import Gameplay
from states.results import ResultsScreen
from states.debug import DebugDisplay


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("BLOOMED")
        self.clock = pygame.time.Clock()
        self.dt = 0

        self.states = {
            "MAIN_MENU": MainMenu(),
            "SONG_SELECT": SongSelect(),
            "LOADING": LoadingScreen(),
            "GAMEPLAY": Gameplay(),
            "RESULTS": ResultsScreen(),
        }
        self.state_name = "MAIN_MENU"
        self.state = self.states[self.state_name]

        # --- NEW: Debug Overlay ---
        self.debug_display = DebugDisplay(self)

    def event_loop(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.state.quit = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                self.debug_display.toggle()

            self.state.get_event(event)

    def flip_state(self):

        current_state = self.state_name
        next_state = self.state.next_state
        self.state.done = False


        persistent_data = self.state.persist

        self.state_name = next_state
        self.state = self.states[self.state_name]


        self.state.startup(persistent_data)

    def update(self):
        if self.state.quit:
            pygame.quit()
            sys.exit()
        elif self.state.done:
            self.flip_state()
        self.state.update(self.dt)

    def draw(self):

        self.state.draw(self.screen)


        self.debug_display.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while True:
            self.event_loop()
            self.update()
            self.draw()
            self.dt = self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()

