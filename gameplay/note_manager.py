import pygame
from settings import *
from gameplay.context import GameContext
from gameplay.note import Note
from utils import draw_text

KEY_MAP = {0: pygame.K_d, 1: pygame.K_f, 2: pygame.K_j, 3: pygame.K_k}
TIMING_WINDOWS = {"perfect": 22, "great": 45, "good": 90, "bad": 120, "miss": 150}
JUDGEMENT_COLORS = {"perfect": (80, 220, 255), "great": (100, 255, 100), "good": (255, 230, 80), "bad": (255, 100, 80),
                    "miss": (200, 200, 200)}


class NoteManager:
    def __init__(self, context: GameContext):
        self.context = context
        self.notes_to_spawn = sorted(self.context.notes, key=lambda n: n.time)
        self.active_notes = []

        self.font_judgement = pygame.font.Font(None, 48)
        self.font_combo = pygame.font.Font(None, 64)
        self.judgement_text = ""
        self.judgement_alpha = 0
        self.judgement_color = WHITE

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            for lane, key in KEY_MAP.items():
                if event.key == key:
                    self.handle_hit(lane)

    def update(self, dt):
        dt_seconds = dt / 1000.0

        spawn_window = (self.context.screen_rect.height / (NOTE_SPEED * 100))
        while self.notes_to_spawn and self.notes_to_spawn[0].time <= self.context.song_time + spawn_window:
            self.active_notes.append(self.notes_to_spawn.pop(0))

        notes_to_remove = []
        for note in self.active_notes:
            time_diff = self.context.song_time - note.time

            if not note.is_hit and not note.is_missed and time_diff * 1000 > TIMING_WINDOWS["miss"]:
                note.is_missed = True
                self.context.judgements['miss'] += 1
                self.context.combo = 0
                self.context.hits += 1
                self.show_judgement("miss")

            note.y_pos = (time_diff * (NOTE_SPEED * 100)) + RECEPTOR_Y

            if note.is_hit or note.y_pos > self.context.screen_rect.height + 50:
                notes_to_remove.append(note)

        self.active_notes = [n for n in self.active_notes if n not in notes_to_remove]

        if self.judgement_alpha > 0:
            self.judgement_alpha = max(0, self.judgement_alpha - (300 * dt_seconds))

    def draw(self, surface):
        playfield_x_start = (self.context.screen_rect.width - (LANE_WIDTH * LANES)) / 2
        for note in self.active_notes:
            if not note.is_hit:
                x = playfield_x_start + (note.lane + 0.5) * LANE_WIDTH
                note_rect = pygame.Rect(0, 0, LANE_WIDTH - 4, 20)
                note_rect.center = (int(x), int(note.y_pos))
                pygame.draw.rect(surface, WHITE, note_rect, border_radius=4)

        if self.context.combo > 2:
            combo_pos = (self.context.screen_rect.centerx, self.context.screen_rect.centery - 100)
            draw_text(surface, str(self.context.combo), combo_pos, self.font_combo, WHITE, text_rect_origin='center')

        if self.judgement_alpha > 0:
            judgement_pos = (self.context.screen_rect.centerx, self.context.screen_rect.centery)
            color_with_alpha = (*self.judgement_color, int(self.judgement_alpha))
            draw_text(surface, self.judgement_text, judgement_pos, self.font_judgement, color_with_alpha,
                      text_rect_origin='center')

    def handle_hit(self, lane):
        for note in self.active_notes:
            if not note.is_hit and not note.is_missed and note.lane == lane:
                time_diff = abs(self.context.song_time - note.time) * 1000

                for judgement, window in TIMING_WINDOWS.items():
                    if time_diff <= window:
                        if judgement != "miss":
                            note.is_hit = True
                            self.context.judgements[judgement] += 1
                            self.context.combo += 1
                            self.context.max_combo = max(self.context.max_combo, self.context.combo)
                            self.context.hits += 1

                            # --- FIX: Add score calculation ---
                            # Add a base score for the hit plus a bonus for the current combo
                            self.context.score += 300 + (20 * self.context.combo)

                            self.show_judgement(judgement)
                        return
                return

    def show_judgement(self, judgement):
        self.judgement_text = judgement.upper()
        self.judgement_color = JUDGEMENT_COLORS.get(judgement, WHITE)
        self.judgement_alpha = 255

