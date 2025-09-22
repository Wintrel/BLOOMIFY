import pygame


class BaseState:
    """
    The base class for all game states, now with transition handling.
    """

    def __init__(self):
        self.done = False
        self.quit = False
        self.next_state = None
        self.screen_rect = pygame.display.get_surface().get_rect()
        self.persist = {}
        self.font = pygame.font.Font(None, 48)

        # --- Transition System ---
        self.transition_state = "normal"  # Can be "in", "out", or "normal"
        self.transition_timer = 0
        self.transition_duration = 0.5  # Default duration in seconds
        self.transition_alpha = 255

    def startup(self, persistent):
        """Called when a state resumes being active."""
        self.persist = persistent
        self.start_transition_in()  # Automatically start the 'in' transition

    def get_event(self, event):
        """Handle a single event passed by the Game object."""
        if event.type == pygame.QUIT:
            self.quit = True

    def start_transition_in(self):
        self.transition_state = "in"
        self.transition_timer = self.transition_duration

    def start_transition_out(self):
        self.transition_state = "out"
        self.transition_timer = self.transition_duration

    def trigger_transition_out(self, next_state=None):
        """ Call this from a state to begin its exit transition. """
        if self.transition_state == "normal":
            self.start_transition_out()
            if next_state:
                self.next_state = next_state

    def update_transition(self, dt_seconds):
        if self.transition_state != "normal":
            self.transition_timer -= dt_seconds
            if self.transition_timer <= 0:
                if self.transition_state == "out":
                    self.done = True  # Signal to the main loop that we are finished
                self.transition_state = "normal"
                self.transition_timer = 0

        # Calculate alpha for fading
        if self.transition_duration > 0:
            progress = 1 - (self.transition_timer / self.transition_duration)
            if self.transition_state == "in":
                self.transition_alpha = int(255 * progress)
            elif self.transition_state == "out":
                self.transition_alpha = int(255 * (1 - progress))
            else:
                self.transition_alpha = 255
        else:
            self.transition_alpha = 255

    def update(self, dt):
        """Update the state. dt is the time since last frame in milliseconds."""
        dt_seconds = dt / 1000.0
        self.update_transition(dt_seconds)

    def draw(self, surface):
        """Draw everything to the screen."""
        pass
