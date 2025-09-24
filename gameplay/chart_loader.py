import json
import os
from gameplay.note import Note


class Chart:
    """ Holds all the data for a single loaded beatmap. """

    def __init__(self):
        self.metadata = {}
        self.notes = []
        self.mechanic_triggers = []


def load_chart(beatmap_path):
    """
    Loads a beatmap.json file and parses it into a Chart object.
    Returns a Chart object or None if loading fails.
    """
    if not beatmap_path or not os.path.exists(beatmap_path):
        print(f"Error: Chart file not found at '{beatmap_path}'")
        return None

    try:
        with open(beatmap_path, 'r') as f:
            data = json.load(f)

        chart = Chart()

        # --- Metadata ---
        chart.metadata = {
            "title": data.get("title", "Unknown"),
            "artist": data.get("artist", "Unknown"),
            "mapper": data.get("mapper", "Unknown"),
            "bpm": data.get("bpm", 120)
        }

        # --- Parse Notes ---
        for note_data in data.get("notes", []):
            time_in_seconds = note_data["time"] / 1000.0
            note = Note(time_in_seconds, note_data["lane"])
            chart.notes.append(note)

        # Sort notes by time, which is crucial for the engine
        chart.notes.sort(key=lambda n: n.time)

        # --- Parse Mechanics (placeholder for now) ---
        chart.mechanic_triggers = data.get("mechanics", [])

        return chart

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing chart file '{beatmap_path}': {e}")
        return None
