import json
from gameplay.note import Note


class Chart:
    """ A simple container for all the data loaded from a beatmap file. """

    def __init__(self, metadata, notes):
        self.metadata = metadata
        self.notes = notes


def load_chart(file_path):
    """ Loads a chart from a .json file, now with hold note support. """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        metadata = {
            "title": data.get("title", "N/A"),
            "artist": data.get("artist", "N/A"),
            "mapper": data.get("mapper", "N/A"),
        }

        notes = []
        for note_data in data.get("notes", []):
            notes.append(Note(
                time=note_data["time"] / 1000.0,
                lane=note_data["lane"],
                # Read the optional 'duration'. Default to 0 if not present.
                duration=note_data.get("duration", 0) / 1000.0
            ))

        return Chart(metadata, notes)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading chart '{file_path}': {e}")
        return None

