import pygame
from settings import *


class Slider:
    """ A draggable slider widget for settings like volume. """

    def __init__(self, pos, size, min_val=0, max_val=1, initial_val=0.5, on_value_changed=None):
        self.rect = pygame.Rect(pos, size)
        self.min_val = min_val
        self.max_val = max_val
        self.on_value_changed = on_value_changed

        self.handle_radius = size[1] // 2 + 4  # Make handle slightly larger than track
        self.is_dragging = False

        # --- FIX: Use a dedicated surface for clean anti-aliasing ---
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.handle_surface = pygame.Surface((self.handle_radius * 2, self.handle_radius * 2), pygame.SRCALPHA)

        self.set_value(initial_val)

    def get_value(self):
        return self.current_val

    def set_value(self, value):
        self.current_val = max(self.min_val, min(self.max_val, value))
        self._update_handle_pos()
        if self.on_value_changed:
            self.on_value_changed(self.current_val)

    def _update_handle_pos(self):
        value_range = self.max_val - self.min_val
        if value_range == 0:
            value_ratio = 0
        else:
            value_ratio = (self.current_val - self.min_val) / value_range

        track_width = self.rect.width - self.handle_radius * 2
        self.handle_pos_x = self.handle_radius + track_width * value_ratio

    def get_event(self, event):
        # Use absolute rect for collision detection
        absolute_rect = self.rect
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if absolute_rect.collidepoint(mouse_pos):
                self.is_dragging = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

        if self.is_dragging and event.type == pygame.MOUSEMOTION:
            # Convert mouse x to be relative to the slider's track
            relative_mouse_x = mouse_pos[0] - (absolute_rect.x + self.handle_radius)
            track_width = absolute_rect.width - 2 * self.handle_radius

            value_ratio = relative_mouse_x / track_width
            new_value = self.min_val + value_ratio * (self.max_val - self.min_val)
            self.set_value(new_value)

    def draw(self, surface):
        # --- Redraw the slider onto its dedicated surface for perfect anti-aliasing ---
        self.surface.fill((0, 0, 0, 0))  # Clear the surface

        # Draw track
        track_height = self.rect.height
        track_rect = pygame.Rect(0, 0, self.rect.width, track_height)
        pygame.draw.rect(self.surface, (30, 30, 40), track_rect, border_radius=int(track_height / 2))

        # Draw fill
        fill_width = self.handle_pos_x
        if fill_width > 0:
            fill_rect = pygame.Rect(0, 0, fill_width, track_height)
            pygame.draw.rect(self.surface, (80, 120, 200), fill_rect, border_radius=int(track_height / 2))

        # Blit the final slider track onto the main screen
        surface.blit(self.surface, self.rect.topleft)

        # Draw the handle on top
        handle_center_y = self.rect.centery
        pygame.draw.circle(surface, (220, 220, 220), (int(self.rect.x + self.handle_pos_x), handle_center_y),
                           self.handle_radius)

