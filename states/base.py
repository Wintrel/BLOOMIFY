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

        # --- Transition Attributes ---
        self.transition_time = 0.5  # 0.5 seconds for fade in/out
        self.transition_timer = 0.0
        self.transition_state = "in"  # Can be "in", "static", or "out"
        self.transition_alpha = 0

    def startup(self, persistent):
        """Called when a state resumes being active."""
        self.persist = persistent
        self.transition_state = "in"
        self.transition_timer = self.transition_time

    def get_event(self, event):
        """Handle a single event passed by the Game object."""
        if event.type == pygame.QUIT:
            self.quit = True

    def go_to_next_state(self):
        """Starts the fade-out transition."""
        self.transition_state = "out"
        self.transition_timer = self.transition_time

    def get_transition_alpha(self):
        """Calculates the current alpha value for UI elements during transitions."""
        return self.transition_alpha

    def update(self, dt):
        """Update the state, including the transition animations."""
        dt_seconds = dt / 1000.0

        if self.transition_state == "in":
            self.transition_timer -= dt_seconds
            if self.transition_timer <= 0:
                self.transition_timer = 0
                self.transition_state = "static"
            self.transition_alpha = 255 * (1 - (self.transition_timer / self.transition_time))

        elif self.transition_state == "out":
            self.transition_timer -= dt_seconds
            if self.transition_timer <= 0:
                self.transition_timer = 0
                self.done = True  # Signal to the main loop that we are finished
            self.transition_alpha = 255 * (self.transition_timer / self.transition_time)

        elif self.transition_state == "static":
            self.transition_alpha = 255

    def draw(self, surface):
        """Draw everything to the screen."""
        pass

