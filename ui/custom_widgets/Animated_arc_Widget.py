import pygame
import math

class AnimatedArc:
    """
    A custom widget to draw and animate a circular arc with optional glow.
    """

    def __init__(self, pos, size, width=10, color=(255, 255, 255),
                 speed=0, start_angle=0, fill_percent=0, glow_color=None):
        min_dim = min(size)
        self.rect = pygame.Rect(0, 0, min_dim, min_dim)
        self.rect.center = (pos[0] + size[0]/2, pos[1] + size[1]/2)

        self.width = width
        self.color = color
        self.speed = speed
        self.current_angle = start_angle
        self.fill_percent = fill_percent
        self.animation_mode = 'spin' if speed != 0 else 'fill'

        # Glow support
        self.glow_color = glow_color or color
        self.glow_alpha = 150  # starting glow intensity

    def update(self, dt):
        if self.animation_mode == 'spin':
            dt_seconds = dt / 1000.0
            self.current_angle += self.speed * dt_seconds

    def set_fill_percent(self, percent):
        self.fill_percent = max(0, min(100, percent))

    def set_glow_alpha(self, alpha):
        self.glow_alpha = max(0, min(255, alpha))

    def draw(self, surface):
        start_angle_rad = math.radians(90 - (self.fill_percent / 100) * 360)
        end_angle_rad = math.radians(90)

        # Draw main arc
        if self.animation_mode == 'spin':
            start_rad = math.radians(self.current_angle)
            end_rad = math.radians(self.current_angle + 270)
            pygame.draw.arc(surface, self.color, self.rect, start_rad, end_rad, self.width)
        elif self.animation_mode == 'fill' and self.fill_percent > 0.5:
            pygame.draw.arc(surface, self.color, self.rect, start_angle_rad, end_angle_rad, self.width)

        # Draw glow overlay
        glow_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.arc(glow_surf, (*self.glow_color, self.glow_alpha),
                        glow_surf.get_rect(), start_angle_rad, end_angle_rad, self.width)
        surface.blit(glow_surf, self.rect.topleft)
