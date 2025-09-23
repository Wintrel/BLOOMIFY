import pygame
from settings import *


def draw_text(surface, text, pos, font, color, text_rect_origin='center', alpha=None, outline_width=0,
              outline_color=BLACK):
    """
    A comprehensive text drawing function that handles alignment, alpha, and outlines.

    Args:
        surface (pygame.Surface): The surface to draw on.
        text (str): The text to render.
        pos (tuple): The (x, y) coordinates for positioning.
        font (pygame.font.Font): The font to use.
        color (tuple): The fill color of the text (RGB or RGBA).
        text_rect_origin (str): The anchor point of the text rect (e.g., 'center', 'topleft').
        alpha (int, optional): Overrides the alpha value of the color. Defaults to None.
        outline_width (int): The thickness of the outline.
        outline_color (tuple): The color of the outline (RGB).
    """
    text_str = str(text)

    # Handle color and alpha
    final_color = color
    final_alpha = alpha if alpha is not None else (color[3] if len(color) == 4 else 255)

    # Render the main text surface
    text_surface = font.render(text_str, True, final_color)
    text_surface.set_alpha(final_alpha)
    text_rect = text_surface.get_rect()
    setattr(text_rect, text_rect_origin, pos)  # Dynamically set position anchor

    # Render the outline if requested
    if outline_width > 0:
        outline_surface = font.render(text_str, True, outline_color)
        outline_surface.set_alpha(final_alpha)

        # Blit the outline from multiple offsets to create thickness
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    outline_pos = (text_rect.x + dx, text_rect.y + dy)
                    surface.blit(outline_surface, outline_pos)

    # Blit the main text on top
    surface.blit(text_surface, text_rect)


def get_dominant_color(image, default_color=(128, 128, 128)):
    """
    Finds the dominant color of a pygame.Surface by scaling it to 1x1.
    Returns only the RGB part of the color.
    """
    if not image:
        return default_color
    try:
        # Scale the image to 1x1 pixel to find the average color
        scaled_image = pygame.transform.smoothscale(image, (1, 1))
        # Get the color of that single pixel
        color = scaled_image.get_at((0, 0))
        return (color.r, color.g, color.b)  # Return as 3-part RGB tuple
    except Exception:
        return default_color


def ensure_vibrant_color(rgb_color, min_saturation=0.5, min_brightness=0.5):
    """
    Takes an RGB color and ensures it's not too dark or desaturated.
    Converts RGB to HSV, adjusts saturation/brightness, and converts back.
    """
    r, g, b = [x / 255.0 for x in rgb_color]
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c

    # Calculate Brightness (Value)
    v = max_c

    # Calculate Saturation
    s = 0 if max_c == 0 else diff / max_c

    # Calculate Hue
    h = 0
    if diff != 0:
        if max_c == r:
            h = (g - b) / diff
        elif max_c == g:
            h = 2 + (b - r) / diff
        else:
            h = 4 + (r - g) / diff
    h = (h * 60) % 360

    # Adjust Saturation and Brightness
    s = max(s, min_saturation)
    v = max(v, min_brightness)

    # --- Convert back to RGB ---
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r_p, g_p, b_p = c, x, 0
    elif 60 <= h < 120:
        r_p, g_p, b_p = x, c, 0
    elif 120 <= h < 180:
        r_p, g_p, b_p = 0, c, x
    elif 180 <= h < 240:
        r_p, g_p, b_p = 0, x, c
    elif 240 <= h < 300:
        r_p, g_p, b_p = x, 0, c
    else:
        r_p, g_p, b_p = c, 0, x

    final_r = int((r_p + m) * 255)
    final_g = int((g_p + m) * 255)
    final_b = int((b_p + m) * 255)

    return (final_r, final_g, final_b)


def scale_to_cover(image, target_size):
    """
    Scales an image to fill a target area while maintaining aspect ratio,
    cropping any excess.
    """
    target_width, target_height = target_size
    img_width, img_height = image.get_size()

    img_aspect = img_width / img_height
    target_aspect = target_width / target_height

    if img_aspect > target_aspect:
        # Image is wider than target, scale to target height
        scale_factor = target_height / img_height
    else:
        # Image is taller than target, scale to target width
        scale_factor = target_width / img_width

    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)

    scaled_img = pygame.transform.smoothscale(image, (new_width, new_height))

    # Create a new surface with the target size and blit the scaled image, centering it.
    final_surface = pygame.Surface(target_size, pygame.SRCALPHA)
    blit_pos = ((target_width - new_width) // 2, (target_height - new_height) // 2)
    final_surface.blit(scaled_img, blit_pos)

    return final_surface

