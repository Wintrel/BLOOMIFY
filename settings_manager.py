import pygame
import json
import os

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "master_volume": 0.5,
    # Add other settings here in the future (e.g., keybinds, resolution)
}

# This will hold the live settings for the game
SETTINGS = {}


def load_settings():
    """ Loads settings from settings.json or creates it with defaults. """
    global SETTINGS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                SETTINGS = json.load(f)
            # Ensure all default keys are present
            for key, value in DEFAULT_SETTINGS.items():
                if key not in SETTINGS:
                    SETTINGS[key] = value
        except (json.JSONDecodeError, TypeError):
            print(f"Warning: Could not read '{SETTINGS_FILE}'. Resetting to defaults.")
            SETTINGS = DEFAULT_SETTINGS.copy()
    else:
        SETTINGS = DEFAULT_SETTINGS.copy()

    # Apply the initial volume setting
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
    level = max(0.0, min(1.0, level))  # Clamp between 0 and 1
    SETTINGS["master_volume"] = level
    apply_volume()


def apply_volume():
    """ Sets the Pygame mixer volume from the current settings. """
    volume = SETTINGS.get("master_volume", 0.5)
    pygame.mixer.music.set_volume(volume)
