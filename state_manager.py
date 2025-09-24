from states.main_menu_state import MainMenuState
from states.song_select_state import SongSelectState
from states.loading_state import LoadingState
from states.results_state import ResultsState
from states.gameplay_state import GameplayState

class StateManager:
    def __init__(self):
        self.states = {
            "MAIN_MENU": MainMenuState(self),
            "SONG_SELECT": SongSelectState(self),
            "LOADING": LoadingState(self),
            "GAMEPLAY": GameplayState(self),
            "RESULTS": ResultsState(self),
        }
        self.state_name = "MAIN_MENU"
        self.state = self.states[self.state_name]
        self.state.startup({})

    def get_event(self, event):
        self.state.get_event(event)

    def update(self, dt):
        if self.state.done:
            self.flip_state()
        self.state.update(dt)

    def draw(self, surface):
        self.state.draw(surface)

    def flip_state(self):
        previous_state_persist = self.state.persist
        self.state.done = False
        self.state_name = self.state.next_state
        self.state = self.states[self.state_name]
        self.state.startup(previous_state_persist)

    def is_done(self):
        """
        Checks if the current state has signaled to quit the entire game.
        """
        return self.state.quit

