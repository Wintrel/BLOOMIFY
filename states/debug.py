import pygame
from settings import *
from .utility import draw_text


class DebugDisplay:
    """
    A special class to handle drawing debug information.
    This is not a full state, but an overlay that can be drawn on top of any state.
    """

    def __init__(self, game_instance):
        self.game = game_instance
        self.font = pygame.font.Font(None, 24)
        self.active = False

    def toggle(self):
        """ Turns the debug display on or off. """
        self.active = not self.active

    def draw(self, surface):
        """ Draws the debug info onto the screen if active. """
        if not self.active:
            return

        # --- Get all the debug information ---
        fps = f"FPS: {self.game.clock.get_fps():.2f}"
        current_state = f"Current State: {self.game.state_name}"
        dt = f"Delta Time: {self.game.dt} ms"

        # --- State-specific debug info ---
        debug_lines = [fps, current_state, dt]

        if self.game.state_name == "GAMEPLAY":
            game_state = self.game.state
            raw_notes_count = len(game_state.persist.get("beatmap_notes", []))
            parsed_notes_count = len(game_state.notes)
            active_notes_count = len(game_state.active_notes)
            song_time = f"Song Time: {game_state.song_time:.2f}s"

            debug_lines.append("-" * 20)  # Separator
            debug_lines.append(f"Raw Notes Loaded: {raw_notes_count}")
            debug_lines.append(f"Gameplay Notes Parsed: {parsed_notes_count}")
            debug_lines.append(f"Active Notes Onscreen: {active_notes_count}")
            debug_lines.append(song_time)

        # --- Draw the information ---
        # Find the longest line to size the background correctly
        max_width = 0
        for line in debug_lines:
            text_surf = self.font.render(line, True, WHITE)
            if text_surf.get_width() > max_width:
                max_width = text_surf.get_width()

        bg_height = len(debug_lines) * 25 + 10
        bg_width = max_width + 20
        bg_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 150))
        surface.blit(bg_surf, (10, 10))

        # Draw each line of text
        for i, line in enumerate(debug_lines):
            draw_text(surface, line, (15, 15 + i * 25), self.font, WHITE, text_rect_origin='topleft')

