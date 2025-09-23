import pygame
import math
from .base import BaseState
from settings import *
from .utility import draw_text


class ResultsScreen(BaseState):
    def __init__(self):
        super(ResultsScreen, self).__init__()
        self.next_state = "SONG_SELECT"

        # Fonts
        self.font_grade = pygame.font.Font(None, 180)
        self.font_score_label = pygame.font.Font(None, 32)
        self.font_score_value = pygame.font.Font(None, 64)
        self.font_judgement = pygame.font.Font(None, 28)
        self.font_info = pygame.font.Font(None, 22)

        self.results_data = {}
        self.background_img = None

    def startup(self, persistent):
        super().startup(persistent)
        self.results_data = self.persist.get("results_data", {})
        song_info = self.results_data.get("song_info", {})

        # Use the blurred background from the gameplay session
        self.background_img = song_info.get("final_background")

    def update(self, dt):
        # This is now required to handle the fade in/out animations
        super().update(dt)

    def get_event(self, event):
        super().get_event(event)
        # Only allow input if the screen is fully visible and not transitioning
        if self.transition_state == "static":
            if event.type == pygame.KEYUP and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                self.go_to_next_state()

    def draw(self, surface):
        if self.background_img:
            surface.blit(self.background_img, (0, 0))
        else:
            surface.fill(BLACK)

        # Create a separate surface for all UI elements to apply the master alpha
        ui_surface = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)

        self.draw_center_panel(ui_surface)

        # Apply the master transition alpha
        ui_surface.set_alpha(self.get_transition_alpha())
        surface.blit(ui_surface, (0, 0))

    def draw_center_panel(self, surface):
        panel_rect = pygame.Rect(0, 0, 800, 500)
        panel_rect.center = self.screen_rect.center
        pygame.draw.rect(surface, (15, 15, 15, 220), panel_rect, border_radius=15)

        # --- Grade ---
        grade = self.results_data.get("grade", "F")
        grade_pos = (panel_rect.centerx, panel_rect.top + 120)
        draw_text(surface, grade, grade_pos, self.font_grade, WHITE, text_rect_origin='center')

        # --- Score ---
        score = self.results_data.get("score", 0)
        score_label_pos = (panel_rect.centerx, panel_rect.top + 230)
        score_value_pos = (panel_rect.centerx, panel_rect.top + 270)
        draw_text(surface, "SCORE", score_label_pos, self.font_score_label, (180, 180, 180), text_rect_origin='center')
        draw_text(surface, f"{score:,}", score_value_pos, self.font_score_value, WHITE, text_rect_origin='center')

        # --- Judgement Counts ---
        judgements = self.results_data.get("judgement_counts", {})
        judgement_order = ["perfect", "great", "good", "bad", "miss"]
        judgement_y = panel_rect.bottom - 100
        total_width = len(judgement_order) * 120
        start_x = panel_rect.centerx - total_width / 2 + 60

        for i, name in enumerate(judgement_order):
            count = judgements.get(name, 0)
            x_pos = start_x + i * 120
            color = JUDGEMENT_COLORS.get(name, WHITE)
            draw_text(surface, name.upper(), (x_pos, judgement_y), self.font_judgement, color,
                      text_rect_origin='center')
            draw_text(surface, str(count), (x_pos, judgement_y + 30), self.font_judgement, WHITE,
                      text_rect_origin='center')

        # --- Back Button Hint ---
        draw_text(surface, "Press Enter to continue", (self.screen_rect.centerx, self.screen_rect.bottom - 40),
                  self.font_info, (150, 150, 150), text_rect_origin='center')

