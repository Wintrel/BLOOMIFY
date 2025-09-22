import pygame
import json
from collections import Counter
from settings import *
from .base import BaseState
from .utility import draw_text, scale_to_cover

# --- Gameplay Constants ---
KEY_MAP = {
    0: pygame.K_d,
    1: pygame.K_f,
    2: pygame.K_j,
    3: pygame.K_k,
}
LANES = 4

# Timing windows in milliseconds
TIMING_WINDOWS = {
    "perfect": 22,
    "great": 45,
    "good": 90,
    "bad": 120,
    "miss": 150
}

JUDGEMENT_COLORS = {
    "perfect": (80, 220, 255),
    "great": (100, 255, 100),
    "good": (255, 230, 80),
    "bad": (255, 100, 80),
    "miss": (200, 200, 200)
}


class Gameplay(BaseState):
    class Note:
        def __init__(self, time, lane):
            self.time = time  # in seconds
            self.lane = lane
            self.y_pos = 0
            self.is_hit = False
            self.is_missed = False

    def __init__(self):
        super(Gameplay, self).__init__()
        self.next_state = "RESULTS"
        self.font_hud = pygame.font.Font(None, 28)
        self.font_combo = pygame.font.Font(None, 64)
        self.font_judgement = pygame.font.Font(None, 48)

    def startup(self, persistent):
        super().startup(persistent)
        self.song_data = self.persist.get("selected_song_data", {})

        # --- Background ---
        unscaled_bg = self.song_data.get("original_img")
        if unscaled_bg:
            self.background_img = scale_to_cover(unscaled_bg, self.screen_rect.size)
            # Add a dark overlay to make notes more visible
            dark_overlay = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 180))
            self.background_img.blit(dark_overlay, (0, 0))
        else:
            self.background_img = pygame.Surface(self.screen_rect.size)
            self.background_img.fill(BLACK)

        # --- Gameplay State ---
        self.song_time = 0.0
        self.notes = []
        self.active_notes = []  # Notes currently on screen
        self.load_beatmap(self.song_data.get("beatmap_path"))

        # --- Scoring ---
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.hits = 0
        self.judgement_counts = Counter()

        # --- Judgement Feedback ---
        self.judgement_text = ""
        self.judgement_alpha = 0
        self.judgement_color = WHITE

    def load_beatmap(self, path):
        if not path: return
        try:
            with open(path, 'r') as f:
                beatmap_data = json.load(f)
                for note_data in beatmap_data.get("notes", []):
                    self.notes.append(self.Note(note_data["time"], note_data["lane"]))
            # Sort notes by time to ensure they spawn correctly
            self.notes.sort(key=lambda n: n.time)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading beatmap {path}: {e}")

    def get_event(self, event):
        super().get_event(event)
        if event.type == pygame.KEYDOWN:
            for lane, key in KEY_MAP.items():
                if event.key == key:
                    self.handle_hit(lane)

    def calculate_accuracy(self):
        if self.hits == 0: return 100.0

        weighted_sum = (
                self.judgement_counts["perfect"] * 1.0 +
                self.judgement_counts["great"] * 0.8 +
                self.judgement_counts["good"] * 0.5 +
                self.judgement_counts["bad"] * 0.2
        )
        return (weighted_sum / self.hits) * 100

    def calculate_grade(self, accuracy):
        if accuracy >= 98: return "S"
        if accuracy >= 95: return "A"
        if accuracy >= 90: return "B"
        if accuracy >= 80: return "C"
        if accuracy >= 70: return "D"
        return "F"

    def handle_hit(self, lane):
        for note in self.active_notes:
            if not note.is_hit and not note.is_missed and note.lane == lane:
                time_diff = abs(self.song_time - note.time) * 1000

                for judgement, window in TIMING_WINDOWS.items():
                    if time_diff <= window:
                        if judgement != "miss":
                            self.score += 300 + (20 * self.combo)
                            self.combo += 1
                            self.max_combo = max(self.max_combo, self.combo)
                            self.hits += 1
                            note.is_hit = True
                            self.show_judgement(judgement)
                        return
                return

    def show_judgement(self, judgement):
        self.judgement_text = judgement.upper()
        self.judgement_color = JUDGEMENT_COLORS.get(judgement, WHITE)
        self.judgement_alpha = 255
        self.judgement_counts[judgement] += 1

    def break_combo(self):
        if self.combo > 0:
            self.combo = 0
        # Misses are handled by the update loop, but we show the text here
        self.show_judgement("miss")
        self.hits += 1  # A miss counts as a hit for accuracy calculation purposes

    def update(self, dt):
        super().update(dt)
        dt_seconds = dt / 1000.0
        self.song_time += dt_seconds

        spawn_window = 1.0
        while self.notes and self.notes[0].time <= self.song_time + spawn_window:
            self.active_notes.append(self.notes.pop(0))

        notes_to_remove = []
        for note in self.active_notes:
            time_diff = self.song_time - note.time

            if not note.is_hit and not note.is_missed and time_diff * 1000 > TIMING_WINDOWS["miss"]:
                note.is_missed = True
                self.break_combo()

            note.y_pos = (time_diff * (NOTE_SPEED * 100)) + RECEPTOR_Y

            if note.is_hit or note.y_pos > self.screen_rect.height + 50:
                notes_to_remove.append(note)

        self.active_notes = [n for n in self.active_notes if n not in notes_to_remove]

        if self.judgement_alpha > 0:
            self.judgement_alpha = max(0, self.judgement_alpha - (300 * dt_seconds))

        if not self.notes and not self.active_notes:
            accuracy = self.calculate_accuracy()
            grade = self.calculate_grade(accuracy)

            self.persist["results_data"] = {
                "score": self.score,
                "accuracy": accuracy,
                "grade": grade,
                "judgement_counts": self.judgement_counts,
                "max_combo": self.max_combo,
                "song_info": self.song_data
            }
            self.done = True

    def draw(self, surface):
        surface.blit(self.background_img, (0, 0))
        self.draw_playfield(surface)
        self.draw_notes(surface)
        self.draw_hud(surface)

    def draw_playfield(self, surface):
        playfield_width = LANE_WIDTH * LANES
        playfield_rect = pygame.Rect(0, 0, playfield_width, self.screen_rect.height)
        playfield_rect.centerx = self.screen_rect.centerx

        s = pygame.Surface((playfield_width, self.screen_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surface.blit(s, playfield_rect)

        for i in range(1, LANES):
            x = playfield_rect.left + i * LANE_WIDTH
            pygame.draw.line(surface, (255, 255, 255, 50), (x, 0), (x, self.screen_rect.height), 2)

        for i in range(LANES):
            x = playfield_rect.left + (i + 0.5) * LANE_WIDTH
            receptor_rect = pygame.Rect(0, 0, LANE_WIDTH, 10)
            receptor_rect.center = (x, RECEPTOR_Y)

            keys = pygame.key.get_pressed()
            color = (255, 255, 255, 200) if keys[KEY_MAP[i]] else (255, 255, 255, 100)
            pygame.draw.rect(surface, color, receptor_rect, border_radius=3)

    def draw_notes(self, surface):
        playfield_x_start = (self.screen_rect.width - (LANE_WIDTH * LANES)) / 2
        for note in self.active_notes:
            if not note.is_hit:
                x = playfield_x_start + (note.lane + 0.5) * LANE_WIDTH
                note_rect = pygame.Rect(0, 0, LANE_WIDTH - 4, 20)
                # --- FIX ---
                # Convert float coordinates to integers to prevent warnings
                note_rect.center = (int(x), int(note.y_pos))
                pygame.draw.rect(surface, WHITE, note_rect, border_radius=4)

    def draw_hud(self, surface):
        score_text = f"{self.score:07d}"
        draw_text(surface, score_text, (20, 20), self.font_hud, WHITE, text_rect_origin='topleft')

        acc_text = f"{self.calculate_accuracy():.2f}%"
        draw_text(surface, acc_text, (self.screen_rect.right - 20, 20), self.font_hud, WHITE,
                  text_rect_origin='topright')

        if self.combo > 2:
            combo_pos = (self.screen_rect.centerx, self.screen_rect.centery - 100)
            # --- FIX ---
            # Convert the combo number to a string before drawing
            draw_text(surface, str(self.combo), combo_pos, self.font_combo, WHITE, text_rect_origin='center')

        if self.judgement_alpha > 0:
            judgement_pos = (self.screen_rect.centerx, self.screen_rect.centery)
            color_with_alpha = (*self.judgement_color, int(self.judgement_alpha))
            draw_text(surface, self.judgement_text, judgement_pos, self.font_judgement, color_with_alpha,
                      text_rect_origin='center')

