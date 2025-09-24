import pygame
import os

# --- Caching Dictionaries ---
IMAGE_CACHE = {}
FONT_CACHE = {}

# --- Paths ---
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_PATH, "assets", "FFonts")
IMAGE_PATH = os.path.join(BASE_PATH, "assets", "images")


def scale_to_cover(image, target_size):
    """
    Scales an image to completely cover a target area while maintaining
    its aspect ratio. The excess is cropped.
    """
    if not image:
        return None

    target_width, target_height = target_size
    image_width, image_height = image.get_size()
    target_ratio = target_width / target_height
    image_ratio = image_width / image_height

    if image_ratio > target_ratio:
        scale_height = target_height
        scale_width = int(scale_height * image_ratio)
    else:
        scale_width = target_width
        scale_height = int(scale_width / image_ratio)

    scaled_image = pygame.transform.smoothscale(image, (scale_width, scale_height))

    final_surface = pygame.Surface(target_size, pygame.SRCALPHA)
    blit_pos_x = (target_width - scale_width) / 2
    blit_pos_y = (target_height - scale_height) / 2
    final_surface.blit(scaled_image, (blit_pos_x, blit_pos_y))
    return final_surface


def load_font(font_name, size):
    cache_key = (font_name, size)
    if cache_key in FONT_CACHE:
        return FONT_CACHE[cache_key]
    if not font_name:
        font = pygame.font.Font(None, size)
        FONT_CACHE[cache_key] = font
        return font
    try:
        full_path = os.path.join(FONT_PATH, f"{font_name}.ttf")
        if not os.path.exists(full_path):
            full_path = os.path.join(FONT_PATH, f"{font_name}.otf")
        font = pygame.font.Font(full_path, size)
        FONT_CACHE[cache_key] = font
        return font
    except (FileNotFoundError, pygame.error) as e:
        print(f"Warning: Font '{font_name}' not found or failed to load. Falling back to default.")
        font = pygame.font.Font(None, size)
        FONT_CACHE[cache_key] = font
        return font


def get_image_path(image_name):
    png_path = os.path.join(IMAGE_PATH, f"{image_name}.png")
    jpg_path = os.path.join(IMAGE_PATH, f"{image_name}.jpg")
    if os.path.exists(png_path): return png_path
    if os.path.exists(jpg_path): return jpg_path
    return None


def load_image(path):
    if path in IMAGE_CACHE:
        return IMAGE_CACHE[path]
    if path and os.path.exists(path):
        try:
            image = pygame.image.load(path).convert_alpha()
            IMAGE_CACHE[path] = image
            return image
        except pygame.error as e:
            print(f"Error loading image '{path}': {e}")
    return None


def create_blurred_background(image, size):
    if not image: return None
    small_size = (size[0] // 20, size[1] // 20)
    scaled_down = pygame.transform.smoothscale(image, small_size)
    blurred = pygame.transform.smoothscale(scaled_down, size)
    dark_overlay = pygame.Surface(size, pygame.SRCALPHA)
    dark_overlay.fill((0, 0, 0, 150))
    blurred.blit(dark_overlay, (0, 0))
    return blurred


def get_dominant_color(image, default_color=(128, 128, 128), vibrant=False):
    if not image: return default_color
    try:
        scaled = pygame.transform.scale(image, (1, 1))
        color = tuple(scaled.get_at((0, 0)))
        if vibrant:
            h, s, v, a = pygame.Color(*color).hsva
            s = max(s, 70)
            v = max(v, 80)
            vibrant_color = pygame.Color(0)
            vibrant_color.hsva = (h, s, v, a)
            return (vibrant_color.r, vibrant_color.g, vibrant_color.b, vibrant_color.a)
        else:
            return color
    except Exception:
        return default_color

