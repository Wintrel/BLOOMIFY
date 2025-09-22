import pygame
import sys
from settings import *
from states.main_menu import MainMenu
from states.song_select import SongSelect
from states.loading import LoadingScreen
from states.gameplay import Gameplay
from states.results import ResultsScreen


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
        self.state.startup({}) # Initial startup for the first state

    def event_loop(self):
        for event in pygame.event.get():
            self.state.get_event(event)

    def flip_state(self):
        # The current state's "out" transition is done, move to the next one
        current_state = self.state_name
        next_state_name = self.state.next_state
        self.state.done = False

        # Manage the persistent data between states
        persistent_data = self.state.persist

        # Get the new state object
        self.state_name = next_state_name
        self.state = self.states[self.state_name]

        # Start the new state with the persistent data
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
        pygame.display.flip()

    def run(self):
        while True:
            self.dt = self.clock.tick(FPS)
            self.event_loop()
            self.update()
            self.draw()

if __name__ == "__main__":
    game = Game()
    game.run()
