from ui.loader import load_layout_from_figma


class UIManager:
    """ Manages the state and drawing of all UI elements for a screen. """

    def __init__(self):
        self.root = None

    def load_layout(self, file_path):
        """ Loads a UI layout from a specified Figma JSON file. """
        self.root = load_layout_from_figma(file_path)

    def get_event(self, event):
        """ Passes events to the root UI element. """
        if self.root:
            self.root.get_event(event)

    def update(self, dt):
        """ Updates the root UI element. """
        if self.root:
            self.root.update(dt)

    def draw(self, surface):
        """ Draws the root UI element. """
        if self.root:
            self.root.draw(surface)

    def get_element_by_name(self, name):
        """
        Finds a specific UI element by its name within the entire UI tree.
        """
        if not self.root:
            return None

        # This is a recursive helper function that will search the tree.
        def find_in_children(element, target_name):
            # Check if the current element is the one we're looking for
            if hasattr(element, 'name') and element.name == target_name:
                return element

            # If not, recursively search through all its children
            if hasattr(element, 'children'):
                for child in element.children:
                    found = find_in_children(child, target_name)
                    if found:
                        return found

            # If not found in this branch, return None
            return None

        return find_in_children(self.root, name)

