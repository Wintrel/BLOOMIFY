from collections import Counter
import pygame
from gameplay.chart_loader import Chart
import settings_manager

class GameContext:
    def __init__(self, chart: Chart, screen_rect: pygame.Rect):
        self.chart = chart
        self.notes = chart.notes if chart else []
        self.start_time_offset = 0
        self.screen_rect = screen_rect
        self.song_time = 0.0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.judgements = Counter(perfect=0, great=0, good=0, bad=0, miss=0)
        self.hits = 0

        # --- Load Keybinds ---
        self.key_map = self.load_keybinds()

    def load_keybinds(self):
        """ Loads key names from settings and converts them to pygame key codes. """
        key_map = {}
        keybinds_from_settings = settings_manager.get_keybinds()
        for i in range(4): # Assuming 4 keys
            key_name = keybinds_from_settings.get(str(i))
            if key_name:
                try:
                    key_map[i] = pygame.key.key_code(key_name)
                except ValueError:
                    print(f"Warning: Invalid key name '{key_name}' in settings.json for lane {i+1}")
        return key_map

    # ... (rest of the GameContext code remains the same)
    def update_time(self, dt_seconds):
        self.song_time += dt_seconds
        if self.song_time < 0:
            self.song_time = 0

    def calculate_accuracy(self):
        if self.hits == 0: return 100.0
        weighted_sum = (self.judgements["perfect"] * 1.0 + self.judgements["great"] * 0.8 + self.judgements["good"] * 0.5 + self.judgements["bad"] * 0.2)
        return (weighted_sum / self.hits) * 100

    def get_results(self):
        accuracy = self.calculate_accuracy()
        if accuracy >= 98: grade = "S"
        elif accuracy >= 95: grade = "A"
        elif accuracy >= 90: grade = "B"
        elif accuracy >= 80: grade = "C"
        elif accuracy >= 70: grade = "D"
        else: grade = "F"
        return {"score": self.score, "accuracy": accuracy, "grade": grade, "judgement_counts": self.judgements, "max_combo": self.max_combo}

