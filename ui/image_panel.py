import pygame
from ui.panel import Panel
import asset_loader


class ImagePanel(Panel):
    """
    A specific type of Panel that can display an image, handling scaling and clipping.
    """

    def __init__(self, name="", pos=(0, 0), size=(0, 0), parent=None):
        super().__init__(name=name, pos=pos, size=size, parent=parent)
        self.image = None

    def set_image(self, image_surface):
        """
        Dynamically sets the panel's image from a pre-loaded pygame.Surface.
        This is used by states to update content (e.g., song artwork).
        """
        if image_surface:
            # Scale the provided image to cover the panel's area without distortion
            self.image = asset_loader.scale_to_cover(image_surface, self.size)
        else:
            self.image = None

    def set_image_from_path(self, image_path):
        """
        Loads an image from a file path and sets it as the panel's image.
        This is primarily used by the UI loader when creating the layout.
        """
        loaded_surface = asset_loader.load_image(image_path)
        self.set_image(loaded_surface)  # Reuse the scaling and setting logic

    def draw(self, surface):
        # First, draw the panel's own background color and border, if any.
        # This is useful for fallbacks or creating frame effects.
        super().draw(surface)

        if self.image:
            rect = pygame.Rect(self.absolute_pos, self.size)

            # To handle rounded corners from Figma, we need to clip the image.
            if self.radius > 0:
                clip_surface = pygame.Surface(self.size, pygame.SRCALPHA)
                # Create the rounded rectangle shape that will be our mask
                pygame.draw.rect(clip_surface, (255, 255, 255, 255), (0, 0, *self.size), border_radius=self.radius)

                # Blit the image, but only where the mask is opaque
                clip_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                surface.blit(clip_surface, rect)
            else:
                # If no radius, just draw the image directly for better performance.
                surface.blit(self.image, rect)

