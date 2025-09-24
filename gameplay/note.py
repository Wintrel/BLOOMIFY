class Note:
    """
    Represents a single note in a beatmap.
    This is a pure data class.
    """
    def __init__(self, time, lane, note_type='normal'):
        self.time = time  # The time in seconds the note should be hit
        self.lane = lane
        self.type = note_type

        # --- Gameplay State ---
        self.is_hit = False
        self.is_missed = False
        self.hit_time_diff = 0  # How early/late the hit was
