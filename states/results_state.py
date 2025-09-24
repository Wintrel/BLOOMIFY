import pygame
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
        self.ui_manager.load_layout("layouts/Results_Layout.json")

        # --- State Data ---
        self.results_data = {}
        self.song_data = {}
        self.background_img = pygame.Surface(self.screen_rect.size)
        self.background_img.fill(BLACK)
        self.score_arc = None

    def startup(self, persistent):
        super().startup(persistent)
        self.results_data = self.persist.get("results_data", {})
        self.song_data = self.persist.get("selected_song_data", {})

        # --- Create blurred background ---
        original_img = asset_loader.load_image(self.song_data.get("image_path"))
        if original_img:
            self.background_img = asset_loader.create_blurred_background(original_img, self.screen_rect.size)

        # --- Populate UI elements with results data ---
        self.populate_ui()

        # --- Setup the animated score arc ---
        placeholder = self.ui_manager.get_element_by_name("score_ellipse")
        if placeholder:
            accent_color = self.song_data.get("accent_color", (255, 255, 255))
            self.score_arc = AnimatedArc(
                pos=placeholder.absolute_pos,
                size=placeholder.size,
                width=28,  # Thickness from your Figma design
                color=accent_color,
                fill_percent=self.results_data.get("accuracy", 0)
            )

    def populate_ui(self):
        """Finds UI elements by name and fills them with dynamic data."""
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
        surface.blit(self.background_img, (0, 0))
        self.ui_manager.draw(surface)
        if self.score_arc:
            self.score_arc.draw(surface)

