class UIElement:
    """
    The base class for all UI elements, now with a visibility flag.
    """

    def __init__(self, name="", pos=(0, 0), size=(0, 0), parent=None):
        self.name = name
        self.pos = list(pos)
        self.size = list(size)
        self.parent = parent
        self.children = []
        self.visible = True  # Add the visibility flag

        self.absolute_pos = [0, 0]
        self._calculate_absolute_pos()

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

    def get_event(self, event):
        for child in self.children:
            child.get_event(event)

    def update(self, dt):
        for child in self.children:
            child.update(dt)

    def draw(self, surface):
        # If this element is not visible, don't draw it or any of its children.
        if not self.visible:
            return

        for child in self.children:
            child.draw(surface)

