import pygame
import sys
from settings import *
from state_manager import StateManager


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("BLOOMIFY")
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = True


        self.state_manager = StateManager()

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
            self.state_manager.get_event(event)

    def update(self):
        self.state_manager.update(self.dt)
        if self.state_manager.is_done():
            self.running = False

    def draw(self):
        self.screen.fill(BLACK)
        self.state_manager.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    game = Game()
    game.run()

