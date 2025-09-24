import pygame

def draw_text(surface, text, center_pos, font, color, alpha=255, outline_width=0, outline_color=(0,0,0), text_rect_origin='center'):
    """
    A powerful text drawing function that handles alpha, alignment, and outlines.
    """
    # Ensure color has an alpha component for proper fading
    if len(color) == 3:
        color = (*color, alpha)
    else:
        color = (color[0], color[1], color[2], alpha)

    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()

    # Handle text alignment
    setattr(text_rect, text_rect_origin, center_pos)

    # Render the outline if requested
    if outline_width > 0:
        mask = pygame.mask.from_surface(font.render(str(text), True, (255,255,255)))
        outline_surface = mask.to_surface(setcolor=outline_color, unsetcolor=(0,0,0,0))
        outline_surface.set_colorkey((0,0,0,0))
        outline_surface.set_alpha(alpha)

        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    surface.blit(outline_surface, (text_rect.x + dx, text_rect.y + dy))

    surface.blit(text_surface, text_rect)
