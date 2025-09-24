import pygame


class BaseState:
    """
    The base class for all game states.
    It handles basic state properties and transition logic.
    """

    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.done = False
        self.quit = False
        self.next_state = None
        self.screen_rect = pygame.display.get_surface().get_rect()
        self.persist = {}  # Data that persists between states
        self.font = pygame.font.Font(None, 48)

        # --- Transition Attributes ---
        self.transition_time = 0.5  # 0.5 seconds for fade in/out
        self.transition_timer = 0.0
        self.transition_state = "in"  # "in", "static", "out"
        self.transition_alpha = 0

    def startup(self, persistent):
        """Called when a state resumes being active."""
        self.persist = persistent
        self.transition_state = "in"
        self.transition_timer = self.transition_time

    def get_event(self, event):
        """Handle a single event."""
        if event.type == pygame.QUIT:
            self.quit = True

    def go_to_next_state(self):
        """Starts the fade-out transition."""
        if self.transition_state == "static":
            self.transition_state = "out"
            self.transition_timer = self.transition_time

    def get_transition_alpha(self):
        """Calculates the current alpha for UI elements during transitions."""
        return self.transition_alpha

    def update(self, dt):
        """Update the state and transition animations."""
        dt_seconds = dt / 1000.0

        if self.transition_state == "in":
            self.transition_timer -= dt_seconds
            if self.transition_timer <= 0:
                self.transition_timer = 0
                self.transition_state = "static"
            # Alpha goes from 0 to 255
            self.transition_alpha = 255 * (1 - (self.transition_timer / self.transition_time))

        elif self.transition_state == "out":
            self.transition_timer -= dt_seconds
            if self.transition_timer <= 0:
                self.transition_timer = 0
                self.done = True  # Signal to the manager that we are finished
            # Alpha goes from 255 to 0
            self.transition_alpha = 255 * (self.transition_timer / self.transition_time)

        elif self.transition_state == "static":
            self.transition_alpha = 255

    def draw(self, surface):
        """Draw everything to the screen."""
        pass
