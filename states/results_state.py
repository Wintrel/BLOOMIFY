import pygame
import math
import time
from settings import *
from states.base_state import BaseState
from ui.ui_manager import UIManager
from ui.custom_widgets.Animated_arc_Widget import AnimatedArc
import asset_loader


class ResultsState(BaseState):
    def __init__(self, state_manager):
        super(ResultsState, self).__init__(state_manager)
        self.next_state = "SONG_SELECT"

        # --- UI Setup ---
        self.ui_manager = UIManager()
        self.ui_manager.load_layout("layouts/results_layout.json")

        # --- State Data ---
        self.results_data = {}
        self.song_data = {}
        self.background_img = pygame.Surface(self.screen_rect.size)
        self.background_img.fill(BLACK)
        self.score_arc = None
        self._display_score = 0  # for animated score counting

    def startup(self, persistent):
        super().startup(persistent)
        self.results_data = self.persist.get("results_data", {})
        self.song_data = self.persist.get("selected_song_data", {})

        # --- Create blurred background ---
        original_img = asset_loader.load_image(self.song_data.get("image_path"))
        if original_img:
            self.background_img = asset_loader.create_blurred_background(
                original_img, self.screen_rect.size
            )
        overlay = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))  # dark overlay
        self.background_img.blit(overlay, (0, 0))

        # --- Populate UI elements ---
        self.populate_ui()

        # --- Setup animated score arc with glow ---
        placeholder = self.ui_manager.get_element_by_name("score_ellipse")
        if placeholder:
            accent_color = self.song_data.get("accent_color", (255, 255, 255))
            self.score_arc = AnimatedArc(
                pos=placeholder.absolute_pos,
                size=placeholder.size,
                width=28,
                color=accent_color,
                fill_percent=self.results_data.get("accuracy", 0),
                glow_color=accent_color
            )

    def populate_ui(self):
        """Populate UI labels with results data."""
        judgements = self.results_data.get("judgement_counts", {})

        ui_map = {
            "score_grade": self.results_data.get("grade", "F"),
            "end_score": f"{self.results_data.get('score', 0):,}",
            "end_accuracy": f"{self.results_data.get('accuracy', 0):.2f}%",
            "beatmaps_name": self.song_data.get("title", "N/A"),
            "beatmapper_name": self.song_data.get("artist", "N/A"),
            "great_judgements": str(judgements.get("perfect", 0)),
            "good_judgement": str(judgements.get("great", 0)),
            "meh_judgement": str(judgements.get("good", 0)),
            "miss_judgement": str(judgements.get("miss", 0))
        }

        for name, text in ui_map.items():
            element = self.ui_manager.get_element_by_name(name)
            if element and hasattr(element, 'set_text'):
                element.set_text(text)

    def get_event(self, event):
        super().get_event(event)
        if self.transition_state == "static":
            if event.type == pygame.MOUSEBUTTONUP:
                back_button = self.ui_manager.get_element_by_name("back_button")
                if back_button and pygame.Rect(back_button.absolute_pos, back_button.size).collidepoint(event.pos):
                    self.go_to_next_state()
            if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
                self.go_to_next_state()

    def draw(self, surface):
        # --- Draw background ---
        surface.blit(self.background_img, (0, 0))

        # --- Animate score counting up ---
        target_score = self.results_data.get("score", 0)
        if self._display_score < target_score:
            self._display_score += max(1, (target_score - self._display_score)//15)
        score_element = self.ui_manager.get_element_by_name("end_score")
        if score_element:
            score_element.set_text(f"{min(self._display_score, target_score):,}")

        # --- Animate grade letter pulse (font size) ---
        grade_element = self.ui_manager.get_element_by_name("score_grade")
        if grade_element:
            base_size = 200  # original font size
            pulse_size = int(base_size + 10 * math.sin(time.time() * 4))
            grade_element.styles['text']['size'] = pulse_size
            grade_element.set_text(self.results_data.get("grade", "F"))

        # --- Animate glowing score arc ---
        if self.score_arc:
            pulse_alpha = int(150 + 50 * math.sin(time.time() * 6))  # pulsing glow
            self.score_arc.set_glow_alpha(pulse_alpha)
            self.score_arc.draw(surface)

        # --- Draw UI elements ---
        self.ui_manager.draw(surface)
