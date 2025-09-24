import pygame
from ui.panel import Panel
from ui.label import Label


class Button(Panel):
    """
    An interactive button element that can be clicked.
    It's a Panel that also contains a Label and handles mouse input.
    """

    def __init__(self, pos, size, color, text, font_size, text_color, hover_color=None, action=None, **kwargs):
        super().__init__(pos, size, color, **kwargs)
        self.text = text
        self.font_size = font_size
        self.text_color = text_color

        # Visual feedback for interaction
        self.base_color = color
        self.hover_color = hover_color if hover_color else [min(c + 30, 255) for c in color[:3]]
        self.is_hovered = False

        # The function to call when the button is clicked
        self.action = action

        # Create a label as a child element
        self.label = Label(self.rect.center, text, font_size, text_color)

    def get_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_hovered and self.action:
                self.action()  # Execute the assigned function

    def update(self, dt):
        # Change color on hover
        if self.is_hovered:
            self.color = self.hover_color
        else:
            self.color = self.base_color

        super().update(dt)

    def draw(self, surface):
        # Draw the panel background first
        super().draw(surface)

        # Then draw the text label on top
        self.label.draw(surface)
