import pygame
from settings import *
from gameplay.context import GameContext

# We can keep KEY_MAP here as it relates to lane input visualization
KEY_MAP = {0: pygame.K_d, 1: pygame.K_f, 2: pygame.K_j, 3: pygame.K_k}


class LaneManager:
    def __init__(self, context: GameContext):
        self.context = context

    def get_event(self, event):
        pass  # The lane manager doesn't need to handle events directly

    def update(self, dt):
        pass  # For now, the lanes are static

    def draw(self, surface):
        # Calculate playfield dimensions based on settings
        playfield_width = LANE_WIDTH * LANES
        playfield_rect = pygame.Rect(0, 0, playfield_width, self.context.screen_rect.height)
        playfield_rect.centerx = self.context.screen_rect.centerx

        # Draw a semi-transparent background for the playfield
        playfield_bg = pygame.Surface(playfield_rect.size, pygame.SRCALPHA)
        playfield_bg.fill((0, 0, 0, 180))
        surface.blit(playfield_bg, playfield_rect)

        # Draw lane separators
        for i in range(1, LANES):
            x = playfield_rect.left + i * LANE_WIDTH
            pygame.draw.line(surface, (255, 255, 255, 50), (x, 0), (x, self.context.screen_rect.height), 2)

        # Draw note receptors
        keys_pressed = pygame.key.get_pressed()
        for i in range(LANES):
            x = playfield_rect.left + (i + 0.5) * LANE_WIDTH
            receptor_rect = pygame.Rect(0, 0, LANE_WIDTH, 10)
            receptor_rect.center = (int(x), RECEPTOR_Y)

            # Light up the receptor if the corresponding key is pressed
            color = (255, 255, 255, 200) if keys_pressed[KEY_MAP[i]] else (255, 255, 255, 100)
            pygame.draw.rect(surface, color, receptor_rect, border_radius=3)

