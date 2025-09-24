import pygame
from ui.ui_element import UIElement


class Panel(UIElement):
    """ A simple UI element that draws a colored rectangle. """

    absolute_pos: list[int]

    def __init__(self, name="", pos=(0, 0), size=(0, 0), parent=None, bg_color=(0, 0, 0, 0), radius=0, border_width=0,
                 border_color=(0, 0, 0, 0)):
        super().__init__(name=name, pos=pos, size=size, parent=parent)
        self.bg_color = bg_color
        self.radius = radius
        self.border_width = border_width
        self.border_color = border_color

    def draw(self, surface):
        rect = pygame.Rect(self.absolute_pos, self.size)

        if self.bg_color and self.bg_color[3] > 0:
            pygame.draw.rect(surface, self.bg_color, rect, border_radius=self.radius)

        if self.border_width > 0 and self.border_color and self.border_color[3] > 0:
            pygame.draw.rect(surface, self.border_color, rect, width=self.border_width, border_radius=self.radius)

        super().draw(surface)  # Draw children

