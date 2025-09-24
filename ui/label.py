import pygame
from ui.ui_element import UIElement
import asset_loader


class Label(UIElement):
    """ A UI element for displaying text. """

    def __init__(self, name="", pos=(0, 0), size=(0, 0), parent=None, text="", font_name=None, font_size=16,
                 color=(255, 255, 255, 255), align="left"):
        super().__init__(name=name, pos=pos, size=size, parent=parent)
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.color = color
        self.align = align
        self.font = None
        self.text_surface = None
        self.create_text_surface()

    def set_text(self, new_text):
        if self.text != new_text:
            self.text = str(new_text)
            self.create_text_surface()

    def create_text_surface(self):
        self.font = asset_loader.load_font(self.font_name, self.font_size)
        if self.font:
            self.text_surface = self.font.render(self.text, True, self.color)

    def draw(self, surface):
        if self.text_surface:
            # --- FIX: Use absolute_pos for drawing ---
            draw_pos = list(self.absolute_pos)

            # Handle text alignment within the element's bounding box
            if self.align == 'center':
                draw_pos[0] += (self.size[0] - self.text_surface.get_width()) // 2
            elif self.align == 'right':
                draw_pos[0] += self.size[0] - self.text_surface.get_width()

            # Vertically center the text
            draw_pos[1] += (self.size[1] - self.text_surface.get_height()) // 2

            surface.blit(self.text_surface, draw_pos)

        super().draw(surface)  # Draw children

