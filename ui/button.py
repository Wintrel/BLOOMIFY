import pygame
from ui.panel import Panel


class Button(Panel):
    """
    An interactive Panel that can be clicked. It now automatically
    generates a hover color.
    """

    def __init__(self, name="", pos=(0, 0), size=(0, 0), parent=None, bg_color=(50, 50, 50, 255), hover_color=None,
                 radius=0, on_click=None):
        super().__init__(name=name, pos=pos, size=size, parent=parent, bg_color=bg_color, radius=radius)

        self.base_color = bg_color

        # If no hover color is provided, create one automatically by brightening the base color.
        if hover_color:
            self.hover_color = hover_color
        else:
            r, g, b, a = self.base_color
            self.hover_color = (min(r + 30, 255), min(g + 30, 255), min(b + 30, 255), a)

        self.on_click = on_click
        self.is_hovered = False

    def get_event(self, event):
        """ Checks for mouse hover and click events. """
        if self.visible:
            if event.type == pygame.MOUSEMOTION:
                self.is_hovered = self.get_rect().collidepoint(event.pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_hovered and self.on_click:
                    self.on_click()

        super().get_event(event)

    def update(self, dt):
        """ Updates background color based on hover state. """
        if self.is_hovered:
            self.bg_color = self.hover_color
        else:
            self.bg_color = self.base_color

        super().update(dt)

    def get_rect(self):
        """ Returns the button's rectangle for collision detection. """
        return pygame.Rect(self.absolute_pos, self.size)

