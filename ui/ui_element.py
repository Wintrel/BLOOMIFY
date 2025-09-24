import pygame


class UIElement:
    """
    The base class for all UI elements, now with a more robust animation engine.
    """

    def __init__(self, name="", pos=(0, 0), size=(0, 0), parent=None):
        self.name = name
        self.pos = list(pos)
        self.size = list(size)
        self.parent = parent
        self.children = []
        self.visible = True
        self.absolute_pos = [0, 0]
        self._calculate_absolute_pos()
        self.is_animating = False
        self.start_pos = list(self.absolute_pos)
        self.target_pos = list(self.absolute_pos)
        self.anim_timer = 0.0
        self.anim_duration = 0.0

    def _calculate_absolute_pos(self):
        if self.parent:
            self.absolute_pos[0] = self.parent.absolute_pos[0] + self.pos[0]
            self.absolute_pos[1] = self.parent.absolute_pos[1] + self.pos[1]
        else:
            self.absolute_pos = list(self.pos)
        for child in self.children:
            child._calculate_absolute_pos()

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
            child.parent = self
            child._calculate_absolute_pos()

    def animate_position(self, target_pos, duration):
        self.start_pos = list(self.absolute_pos)
        self.target_pos = list(target_pos)
        self.anim_duration = duration
        self.anim_timer = 0.0
        self.is_animating = True

    @staticmethod
    def ease_out_cubic(t):
        t -= 1
        return t * t * t + 1

    def update(self, dt):
        if self.is_animating:
            self.anim_timer += dt / 1000.0
            if self.anim_duration > 0:
                progress = min(self.anim_timer / self.anim_duration, 1.0)
                eased_progress = self.ease_out_cubic(progress)
                self.absolute_pos[0] = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * eased_progress
                self.absolute_pos[1] = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * eased_progress

                # --- FIX: After moving, tell children to update their positions ---
                for child in self.children:
                    child._calculate_absolute_pos()

                if progress >= 1.0:
                    self.is_animating = False
            else:
                self.is_animating = False
                self.absolute_pos = list(self.target_pos)
                for child in self.children:
                    child._calculate_absolute_pos()

        for child in self.children:
            child.update(dt)

    def draw(self, surface):
        if not self.visible: return
        for child in self.children:
            child.draw(surface)

    def get_event(self, event):
        for child in self.children:
            child.get_event(event)

