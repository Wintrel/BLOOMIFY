import pygame
from collections import Counter
from settings import *
from .base import BaseState
from .utility import draw_text


class ResultsScreen(BaseState):
    def __init__(self):
        super(ResultsScreen, self).__init__()
        self.next_state = "SONG_SELECT"
        self.score = 0
        self.accuracy = 0
        self.grade = ""
        self.judgement_counts = Counter()
        self.song_info = {}
        self.background_img = None

        # --- Load Fonts ---
        self.font_grade = pygame.font.Font(None, 150)
        self.font_score_label = pygame.font.Font(None, 32)
        self.font_score_value = pygame.font.Font(None, 60)
        self.font_judgement_label = pygame.font.Font(None, 28)
        self.font_judgement_value = pygame.font.Font(None, 36)
        self.font_song_title = pygame.font.Font(None, 48)
        self.font_back_button = pygame.font.Font(None, 24)

    def startup(self, persistent):
        super().startup(persistent)
        results_data = self.persist.get("results_data", {})

        self.score = results_data.get("score", 0)
        self.accuracy = results_data.get("accuracy", 0.0)
        self.grade = results_data.get("grade", "F")
        self.judgement_counts = results_data.get("judgement_counts", Counter())

        # --- BACKGROUND FIX ---
        # Get the song info, which now contains the pre-rendered background.
        self.song_info = results_data.get("song_info", {})
        self.background_img = self.song_info.get("final_background")

    def get_event(self, event):
        super().get_event(event)
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                self.done = True

    def draw(self, surface):
        # --- BACKGROUND FIX ---
        # Draw the blurred background first.
        if self.background_img:
            surface.blit(self.background_img, (0, 0))
        else:
            surface.fill(BLACK)

        # Main panel
        panel_rect = pygame.Rect(0, 0, 700, 450)
        panel_rect.center = self.screen_rect.center
        pygame.draw.rect(surface, (15, 15, 15, 200), panel_rect, border_radius=15)

        # Grade circle
        circle_center = (panel_rect.left + 150, panel_rect.centery)
        pygame.draw.circle(surface, (30, 30, 30), circle_center, 100)
        pygame.draw.circle(surface, WHITE, circle_center, 100, 4)
        draw_text(surface, self.grade, circle_center, self.font_grade, WHITE, text_rect_origin='center')

        # Right-side stats
        stats_x = panel_rect.left + 320

        # Song Title
        title_y = panel_rect.top + 50
        draw_text(surface, self.song_info.get("title", "Unknown Song"), (stats_x, title_y),
                  self.font_song_title, WHITE, text_rect_origin='topleft')

        # Score and Accuracy
        score_y = panel_rect.top + 130
        draw_text(surface, "SCORE", (stats_x, score_y), self.font_score_label, (180, 180, 180),
                  text_rect_origin='topleft')
        draw_text(surface, f"{self.score:07d}", (stats_x, score_y + 25), self.font_score_value, WHITE,
                  text_rect_origin='topleft')

        acc_x = stats_x + 250
        draw_text(surface, "ACCURACY", (acc_x, score_y), self.font_score_label, (180, 180, 180),
                  text_rect_origin='topleft')
        draw_text(surface, f"{self.accuracy:.2f}%", (acc_x, score_y + 25), self.font_score_value, WHITE,
                  text_rect_origin='topleft')

        # Judgement counts
        judgements_y = panel_rect.top + 250
        judgement_order = ["perfect", "great", "good", "bad", "miss"]

        for i, name in enumerate(judgement_order):
            x = stats_x + (i * 110)
            draw_text(surface, name.upper(), (x, judgements_y), self.font_judgement_label, (180, 180, 180),
                      text_rect_origin='topleft')
            draw_text(surface, str(self.judgement_counts.get(name, 0)), (x, judgements_y + 25),
                      self.font_judgement_value, WHITE, text_rect_origin='topleft')

        # Back button hint
        back_text = "Press ENTER to continue"
        back_pos = (self.screen_rect.centerx, self.screen_rect.bottom - 40)
        draw_text(surface, back_text, back_pos, self.font_back_button, (200, 200, 200), text_rect_origin='center')

