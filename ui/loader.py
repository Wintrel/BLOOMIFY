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
        parts = [float(p.strip()) for p in parts_str.split(',')]
        # Convert 0-1 alpha from Figma to 0-255 for Pygame if present
        if len(parts) == 4 and parts[3] <= 1.0:
            parts[3] *= 255

        final_parts = [int(p) for p in parts]
        return tuple(final_parts) + (255,) if len(final_parts) == 3 else tuple(final_parts)
    except (ValueError, TypeError):
        return default_color


def _get_position_from_data(data):
    for key in ['pos', 'position']:
        if key in data and isinstance(data.get(key), dict):
            return [data[key].get('x', 0), data[key].get('y', 0)]
    if 'size' in data and isinstance(data.get('size'), dict) and 'position' in data['size']:
        pos_data = data['size']['position']
        if isinstance(pos_data, dict):
            return [pos_data.get('x', 0), pos_data.get('y', 0)]
    return None


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

    element_class = None
    if name.startswith("IMG_"):
        element_class = ImagePanel
    elif name.endswith("_button"):
        element_class = Button
    else:
        element_class = FIGMA_TO_UI_MAP.get(data.get("type"))

    if not element_class: return None

    size = [data.get("size", {}).get("w", 0), data.get("size", {}).get("h", 0)]
    absolute_pos = _get_position_from_data(data)
    if absolute_pos is None: absolute_pos = [0, 0]

    if parent:
        relative_pos = [absolute_pos[0] - parent.absolute_pos[0], absolute_pos[1] - parent.absolute_pos[1]]
    else:
        relative_pos = absolute_pos

    element_args = {'name': name, 'pos': relative_pos, 'size': size, 'parent': parent}
    styles = data.get("styles", {})

    if issubclass(element_class, Panel):
        element_args['bg_color'] = _parse_figma_color(styles.get("bg"))
        element_args['radius'] = int(styles.get("radius", 0))
        border = styles.get("border", {})
        if border:
            element_args['border_width'] = int(border.get("width", 0))
            element_args['border_color'] = _parse_figma_color(border.get("color"))

    element = element_class(**element_args)

    if isinstance(element, Label):
        element.set_text(data.get("content", ""))
        text_styles = styles.get("text", {})
        element.font_size = int(text_styles.get("size", 16))
        element.font_name = text_styles.get("family")
        element.align = text_styles.get("align", "left").lower()

        # --- FIX: Prioritize text color from the nested "text" style object ---
        if 'color' in text_styles:
            element.color = _parse_figma_color(text_styles.get("color"), (255, 255, 255, 255))
        else:  # Fallback to the main 'bg' color
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

