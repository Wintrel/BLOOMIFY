import pygame
import math


class AnimatedArc:
    """
    A custom widget to draw and animate a circular arc.
    """

    def __init__(self, pos, size, width=10, color=(255, 255, 255), speed=0, start_angle=0, fill_percent=0):
        # Ensure the arc is always a circle by creating a square bounding box
        min_dim = min(size)
        self.rect = pygame.Rect(0, 0, min_dim, min_dim)
        self.rect.center = (pos[0] + size[0] / 2, pos[1] + size[1] / 2)

        self.width = width
        self.color = color
        self.speed = speed
        self.current_angle = start_angle
        self.fill_percent = fill_percent
        self.animation_mode = 'spin' if speed != 0 else 'fill'

    def update(self, dt):
        """ Animate the arc's angle if it's in spin mode. """
        if self.animation_mode == 'spin':
            dt_seconds = dt / 1000.0
            self.current_angle += self.speed * dt_seconds

    def set_fill_percent(self, percent):
        """ Instantly sets the fill percentage for the arc. """
        self.fill_percent = max(0, min(100, percent))

    def draw(self, surface):
        """ Draw the arc to a surface. """
        if self.animation_mode == 'spin':
            # Draw a 270-degree arc for the loading spinner
            start_rad = math.radians(self.current_angle)
            end_rad = math.radians(self.current_angle + 270)
            pygame.draw.arc(surface, self.color, self.rect, start_rad, end_rad, self.width)

        elif self.animation_mode == 'fill':
            if self.fill_percent > 0.5:  # Don't draw a tiny dot for 0%
                # --- FIX: Correct angle calculation for a clockwise fill from the top ---
                fill_degrees = (self.fill_percent / 100) * 360
                # Pygame draws counter-clockwise, so we define the arc from its end to its start
                start_angle_rad = math.radians(90 - fill_degrees)
                end_angle_rad = math.radians(90)

                pygame.draw.arc(surface, self.color, self.rect, start_angle_rad, end_angle_rad, self.width)

