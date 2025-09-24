import json
import pygame
from ui.ui_element import UIElement
from ui.label import Label
from ui.panel import Panel
from ui.button import Button
from ui.image_panel import ImagePanel
import asset_loader

FIGMA_TO_UI_MAP = {
    "RECTANGLE": Panel, "TEXT": Label, "GROUP": UIElement,
    "FRAME": UIElement, "ELLIPSE": Panel
}


def _parse_figma_color(color_string, default_color=(0, 0, 0, 0)):
    if not isinstance(color_string, str): return default_color
    try:
        parts_str = color_string.lower().strip().strip('rgba()').strip('rgb()')
        parts = [int(p.strip()) for p in parts_str.split(',')]
        return tuple(parts) + (255,) if len(parts) == 3 else tuple(parts)
    except (ValueError, TypeError):
        return default_color


def _get_position_from_data(data):
    # This robustly checks for different possible position keys you might add manually
    for key in ['pos', 'position']:
        if key in data and isinstance(data.get(key), dict):
            return [data[key].get('x', 0), data[key].get('y', 0)]
    # Also check for the weird nested position some plugins use
    if 'size' in data and isinstance(data.get('size'), dict) and 'position' in data['size']:
        pos_data = data['size']['position']
        if isinstance(pos_data, dict):
            return [pos_data.get('x', 0), pos_data.get('y', 0)]
    return None  # Return None if no position is found


def load_layout_from_figma(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            layout_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading Figma layout file '{file_path}': {e}")
        return None
    root_structure = layout_data.get("structure")
    if not root_structure: return None
    return _create_element_from_figma_data(root_structure)


def _create_element_from_figma_data(data, parent=None):
    name = data.get("name", "")
    element_class = ImagePanel if name.startswith("IMG_") else FIGMA_TO_UI_MAP.get(data.get("type"))
    if not element_class: return None

    size = [data.get("size", {}).get("w", 0), data.get("size", {}).get("h", 0)]

    # --- POSITIONING LOGIC ---
    absolute_pos = _get_position_from_data(data)

    # If a position is found in the JSON, use it. Otherwise, default to (0,0).
    if absolute_pos is None:
        absolute_pos = [0, 0]

    # Calculate the position of this element RELATIVE to its parent.
    if parent:
        relative_pos = [absolute_pos[0] - parent.absolute_pos[0], absolute_pos[1] - parent.absolute_pos[1]]
    else:
        # If there's no parent, its relative position is its absolute position.
        relative_pos = absolute_pos

    element = element_class(name=name, pos=relative_pos, size=size, parent=parent)
    # The UIElement's __init__ will now correctly calculate the final absolute_pos

    styles = data.get("styles", {})
    if isinstance(element, Panel):
        element.bg_color = _parse_figma_color(styles.get("bg"))
        element.radius = int(styles.get("radius", 0))
        border = styles.get("border", {})
        if border:
            element.border_width = int(border.get("width", 0))
            element.border_color = _parse_figma_color(border.get("color"))

    if isinstance(element, Label):
        element.set_text(data.get("content", ""))
        text_styles = styles.get("text", {})
        element.font_size = int(text_styles.get("size", 16))
        element.font_name = text_styles.get("family")
        element.align = text_styles.get("align", "left").lower()
        element.color = _parse_figma_color(styles.get("bg"), (255, 255, 255, 255))
        element.create_text_surface()

    if isinstance(element, ImagePanel):
        image_name = element.name.replace("IMG_", "")
        element.set_image_from_path(asset_loader.get_image_path(image_name))

    for child_data in data.get("children", []):
        child_element = _create_element_from_figma_data(child_data, parent=element)
        if child_element:
            element.add_child(child_element)

    return element

