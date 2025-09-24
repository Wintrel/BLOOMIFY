import pygame
from ui.panel import Panel
import asset_loader


class ImagePanel(Panel):
    """
    A specific type of Panel that can display an image. It inherits all styling
    properties from Panel, such as background color, radius, and borders.
    """

    def __init__(self, name="", pos=(0, 0), size=(0, 0), parent=None, **kwargs):
        """
        Initializes the ImagePanel. It accepts all arguments that a Panel
        does by using **kwargs.
        """
        # Pass all styling arguments (bg_color, radius, etc.) up to the parent Panel
        super().__init__(name=name, pos=pos, size=size, parent=parent, **kwargs)
        self.image = None

    def set_image(self, image_surface):
        """
        Dynamically sets the panel's image from a pre-loaded pygame.Surface.
        """
        if image_surface:
            self.image = asset_loader.scale_to_cover(image_surface, self.size)
        else:
            self.image = None

    def set_image_from_path(self, image_path):
        """
        Loads an image from a file path and sets it as the panel's image.
        """
        loaded_surface = asset_loader.load_image(image_path)
        self.set_image(loaded_surface)

    def draw(self, surface):
        # First, draw the panel's own background color and border from the parent class.
        super().draw(surface)

        if self.image:
            rect = pygame.Rect(self.absolute_pos, self.size)

            if self.radius > 0:
                clip_surface = pygame.Surface(self.size, pygame.SRCALPHA)
                pygame.draw.rect(clip_surface, (255, 255, 255, 255), (0, 0, *self.size), border_radius=self.radius)
                clip_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                surface.blit(clip_surface, rect)
            else:
                surface.blit(self.image, rect)