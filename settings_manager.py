import pygame
import json
import os

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "master_volume": 0.5,
    "keybinds": {
        "0": "d",
        "1": "f",
        "2": "j",
        "3": "k"
    }
}

SETTINGS = {}


def load_settings():
    """ Loads settings from settings.json or creates it with defaults. """
    global SETTINGS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                SETTINGS = json.load(f)
            # Ensure all default keys and nested keys are present
            for key, value in DEFAULT_SETTINGS.items():
                if key not in SETTINGS:
                    SETTINGS[key] = value
            for key, value in DEFAULT_SETTINGS['keybinds'].items():
                if key not in SETTINGS['keybinds']:
                    SETTINGS['keybinds'][key] = value

        except (json.JSONDecodeError, TypeError):
            SETTINGS = DEFAULT_SETTINGS.copy()
    else:
        SETTINGS = DEFAULT_SETTINGS.copy()

    apply_volume()


def save_settings():
    """ Saves the current settings to settings.json. """
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(SETTINGS, f, indent=4)
    except IOError as e:
        print(f"Error: Could not save settings to '{SETTINGS_FILE}': {e}")


def set_volume(level):
    """ Updates the volume setting and applies it immediately. """
    level = max(0.0, min(1.0, level))
    SETTINGS["master_volume"] = level
    apply_volume()


def apply_volume():
    """ Sets the Pygame mixer volume from the current settings. """
    volume = SETTINGS.get("master_volume", 0.5)
    pygame.mixer.music.set_volume(volume)


def get_keybinds():
    """ Returns the current keybinds dictionary. """
    return SETTINGS.get("keybinds", DEFAULT_SETTINGS["keybinds"])


def set_keybind(lane_index, key_name):
    """ Sets a new key for a specific lane. """
    SETTINGS["keybinds"][str(lane_index)] = key_name
    save_settings()  # Save immediately after changing

