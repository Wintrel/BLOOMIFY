from gameplay.context import GameContext

class MechanicManager:
    def __init__(self, context: GameContext):
        self.context = context
        # This is where we will load and manage our "silly" mechanics
        self.active_mechanics = []

    def get_event(self, event):
        for mechanic in self.active_mechanics:
            mechanic.get_event(event)

    def update(self, dt):
        for mechanic in self.active_mechanics:
            mechanic.update(dt)

    def draw(self, surface):
        for mechanic in self.active_mechanics:
            mechanic.draw(surface)

