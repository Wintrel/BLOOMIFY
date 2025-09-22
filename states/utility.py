import pygame


# noinspection D
def draw_text(surface, text, pos, font, color, text_rect_origin='center',
              outline_width=0, outline_color=(0, 0, 0), outline_only=False):
    """
    A master text drawing function that handles alignment, alpha, outlines, and outline_only.
    - color can be a 3-tuple (RGB) or 4-tuple (RGBA).
    - text_rect_origin controls alignment ('center', 'topleft', 'topright', etc.)
    """
    text_str = str(text)

    # 1. Handle color and alpha
    use_alpha = len(color) == 4
    text_color = color[:3] if use_alpha else color
    alpha = color[3] if use_alpha else 255

    # 2. Render the base text surface to get its dimensions
    text_surface = font.render(text_str, True, text_color)
    text_rect = text_surface.get_rect()
    setattr(text_rect, text_rect_origin, pos)  # Align the rect

    # 3. Draw outline by blitting shifted versions of the text
    if outline_width > 0:
        outline_surface = font.render(text_str, True, outline_color)
        if use_alpha:
            outline_surface.set_alpha(alpha)

        # Blit the outline in a circle around the text
        for angle in range(0, 360, 45):
            radian_angle = pygame.math.Vector2(1, 0).rotate(angle) * outline_width
            outline_pos = (text_rect.x + radian_angle.x, text_rect.y + radian_angle.y)
            surface.blit(outline_surface, outline_pos)

    # 4. Draw the main text fill on top
    if not outline_only:
        if use_alpha:
            text_surface.set_alpha(alpha)
        surface.blit(text_surface, text_rect)


def get_dominant_color(image, default_color=(128, 128, 128)):
    """
    Finds the dominant color of a pygame.Surface by scaling it to 1x1.
    """
    if not image:
        return default_color
    try:
        # Scale the image to 1x1 pixel to get the average color
        scaled_img = pygame.transform.scale(image, (1, 1))
        # Get the color of that single pixel
        color = tuple(scaled_img.get_at((0, 0)))
        return color[:3]  # Return just RGB, ignore alpha
    except pygame.error:
        return default_color


def scale_to_cover(image, target_size):
    """
    Scales an image to completely cover a target area while maintaining aspect ratio.
    Crops the excess from the center.
    """
    target_width, target_height = target_size
    img_width, img_height = image.get_size()

    # Compare aspect ratios
    target_aspect = target_width / target_height
    img_aspect = img_width / img_height

    if img_aspect > target_aspect:
        # Image is wider than target, scale to target height
        scale_factor = target_height / img_height
    else:
        # Image is taller than target, scale to target width
        scale_factor = target_width / img_width

    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)

    scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))

    # Center the scaled image and crop
    crop_rect = pygame.Rect(
        (new_width - target_width) / 2,
        (new_height - target_height) / 2,
        target_width,
        target_height
    )

    final_surface = pygame.Surface(target_size, pygame.SRCALPHA)
    final_surface.blit(scaled_image, (0, 0), crop_rect)
    return final_surface

