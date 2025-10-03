import pygame
from settings import *
from gameplay.context import GameContext
from gameplay.note import Note
from utils import draw_text

TIMING_WINDOWS = {"perfect": 22, "great": 45, "good": 90, "bad": 120, "miss": 150}
JUDGEMENT_COLORS = {"perfect": (80, 220, 255), "great": (100, 255, 100), "good": (255, 230, 80), "bad": (255, 100, 80),
                    "miss": (200, 200, 200)}
HOLD_NOTE_COLOR = (200, 200, 255)
HELD_NOTE_COLOR = (255, 255, 255)


# noinspection D
class NoteManager:
    def __init__(self, context: GameContext):
        self.context = context
        self.notes_to_spawn = sorted(self.context.notes, key=lambda n: n.time)
        self.active_notes = []
        # --- Use dynamic key map from context ---
        self.key_map = self.context.key_map

        self.font_judgement = pygame.font.Font(None, 48)
        self.font_combo = pygame.font.Font(None, 64)
        # ... (rest of __init__ remains the same)
        self.judgement_text = ""
        self.judgement_alpha = 0
        self.judgement_color = WHITE

    # ... (rest of the NoteManager code remains the same, but uses self.key_map instead of KEY_MAP)
    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            for lane, key in self.key_map.items():
                if event.key == key:
                    self.handle_hit(lane)
        elif event.type == pygame.KEYUP:
            for lane, key in self.key_map.items():
                if event.key == key:
                    self.handle_release(lane)

    def update(self, dt):
        dt_seconds = dt / 1000.0
        spawn_window = (self.context.screen_rect.height / (NOTE_SPEED * 100))
        while self.notes_to_spawn and self.notes_to_spawn[0].time <= self.context.song_time + spawn_window:
            self.active_notes.append(self.notes_to_spawn.pop(0))
        keys_pressed = pygame.key.get_pressed()
        notes_to_remove = []
        for note in self.active_notes:
            time_diff = self.context.song_time - note.time
            if not note.is_hit and not note.is_missed:
                if time_diff * 1000 > TIMING_WINDOWS["miss"]:
                    note.is_missed = True
                    self.break_combo()
            if note.is_held:
                if not keys_pressed[self.key_map[note.lane]]:
                    note.is_held = False
                    self.break_combo()
                elif self.context.song_time >= note.end_time:
                    note.is_held = False
                    note.is_hit = True
                    self.context.score += 100
            note.y_pos = (time_diff * (NOTE_SPEED * 100)) + RECEPTOR_Y
            if note.is_hit or note.y_pos > self.context.screen_rect.height + 200:
                notes_to_remove.append(note)
        self.active_notes = [n for n in self.active_notes if n not in notes_to_remove]
        if self.judgement_alpha > 0:
            self.judgement_alpha = max(0, self.judgement_alpha - (300 * dt_seconds))

    def draw(self, surface):
        playfield_x_start = (self.context.screen_rect.width - (LANE_WIDTH * LANES)) / 2
        for note in self.active_notes:
            if note.is_hit: continue
            x = playfield_x_start + (note.lane + 0.5) * LANE_WIDTH
            head_y = note.y_pos
            if note.duration > 0:
                tail_end_y = ((self.context.song_time - note.end_time) * (NOTE_SPEED * 100)) + RECEPTOR_Y
                rect_top = tail_end_y
                rect_bottom = head_y
                if note.is_held:
                    rect_top = max(rect_top, RECEPTOR_Y)
                rect_height = rect_bottom - rect_top
                if rect_height > 0:
                    tail_rect = pygame.Rect(0, 0, LANE_WIDTH - 10, rect_height)
                    tail_rect.midtop = (int(x), int(rect_top))
                    tail_color = HELD_NOTE_COLOR if note.is_held else HOLD_NOTE_COLOR
                    pygame.draw.rect(surface, tail_color, tail_rect, border_radius=5)
            if not note.is_held:
                note_rect = pygame.Rect(0, 0, LANE_WIDTH - 4, 20)
                note_rect.center = (int(x), int(head_y))
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
                            self.context.judgements[judgement] += 1
                            self.context.combo += 1
                            self.context.max_combo = max(self.context.max_combo, self.context.combo)
                            self.context.hits += 1
                            self.context.score += 300 + (20 * self.context.combo)
                            self.show_judgement(judgement)
                            if note.duration > 0:
                                note.is_held = True
                            else:
                                note.is_hit = True
                        return
                return

    def handle_release(self, lane):
        for note in self.active_notes:
            if note.is_held and note.lane == lane:
                if self.context.song_time >= note.end_time:
                    note.is_held = False
                    note.is_hit = True
                else:
                    note.is_held = False
                    self.break_combo()
                return

    def show_judgement(self, judgement):
        self.judgement_text = judgement.upper()
        self.judgement_color = JUDGEMENT_COLORS.get(judgement, WHITE)
        self.judgement_alpha = 255

    def break_combo(self):
        self.context.combo = 0
        self.context.judgements['miss'] += 1
        self.context.hits += 1
        self.show_judgement("miss")

