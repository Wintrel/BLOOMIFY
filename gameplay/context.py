from collections import Counter
import pygame
from gameplay.chart_loader import Chart


class GameContext:
    """
    Holds the shared state of the gameplay. All managers read from and
    write to this single source of truth.
    """

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

    def update_time(self, dt_seconds):
        self.song_time += dt_seconds
        if self.song_time < 0:
            self.song_time = 0

    def calculate_accuracy(self):
        """ Calculates the current accuracy based on judgements. """
        if self.hits == 0:
            return 100.0

        weighted_sum = (
                self.judgements["perfect"] * 1.0 +
                self.judgements["great"] * 0.8 +
                self.judgements["good"] * 0.5 +
                self.judgements["bad"] * 0.2
        )
        # In this model, a 'miss' contributes to 'hits' but has a weight of 0
        return (weighted_sum / self.hits) * 100

    def get_results(self):
        """ Packages up the final results for the ResultsState. """
        accuracy = self.calculate_accuracy()

        if accuracy >= 98:
            grade = "S"
        elif accuracy >= 95:
            grade = "A"
        elif accuracy >= 90:
            grade = "B"
        elif accuracy >= 80:
            grade = "C"
        elif accuracy >= 70:
            grade = "D"
        else:
            grade = "F"

        return {
            "score": self.score,
            "accuracy": accuracy,
            "grade": grade,
            "judgement_counts": self.judgements,
            "max_combo": self.max_combo,
        }

