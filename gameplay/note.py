class Note:
    """
    Defines a single note object, now with support for hold notes.
    """

    def __init__(self, time, lane, duration=0):
        # --- Core Properties ---
        self.time = time  # in seconds
        self.lane = lane
        self.duration = duration  # in seconds. If 0, it's a tap note.

        # --- Gameplay State ---
        self.y_pos = 0
        self.is_hit = False
        self.is_missed = False
        self.is_held = False  # True if the player is currently holding this note

    @property
    def end_time(self):
        """Calculates the time the hold note should be released."""
        return self.time + self.duration

