import pygame
from settings import *
from gameplay.context import GameContext
from utils import draw_text

class HUDManager:
    """
    Manages drawing the Heads-Up Display (score, accuracy, etc.) during gameplay.
    """
    def __init__(self, context: GameContext):
        self.context = context
        self.font_hud = pygame.font.Font(None, 48)

    def get_event(self, event):
        """ The HUD is not interactive, so this method is a placeholder. """
        pass

    def update(self, dt):
        """ The HUD's data is read live from the context, so no updates are needed. """
        pass

    def draw(self, surface):
        """ Draws the score and accuracy to the screen. """
        # --- Draw Score (Top Left) ---
        score_text = f"{self.context.score:07d}"
        draw_text(surface, score_text, (40, 40), self.font_hud, WHITE, text_rect_origin='topleft')

        # --- Draw Accuracy (Top Right) ---
        accuracy = self.context.calculate_accuracy()
        acc_text = f"{accuracy:.2f}%"
        draw_text(surface, acc_text, (self.context.screen_rect.right - 40, 40), self.font_hud, WHITE, text_rect_origin='topright')
