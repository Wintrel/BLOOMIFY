import pygame
from settings import *
from ui.ui_manager import UIManager
from ui.custom_widgets.slider import Slider
from ui.button import Button
from ui.label import Label
import settings_manager


class SettingsMenu:
    def __init__(self):
        self.is_active = False
        self.is_animating = False
        self.ui_manager = UIManager()
        self.ui_manager.load_layout("layouts/settings_menu.json")

        self.settings_panel = self.ui_manager.get_element_by_name("settings_panel")
        if self.settings_panel:
            self.on_screen_pos = list(self.settings_panel.absolute_pos)
            self.off_screen_pos = [-self.settings_panel.size[0], self.on_screen_pos[1]]
            self.settings_panel.absolute_pos = list(self.off_screen_pos)
            self.settings_panel._calculate_absolute_pos()

        # --- Sliders ---
        self.volume_slider = None
        slider_placeholder = self.ui_manager.get_element_by_name("volume_slider_placeholder")
        if slider_placeholder:
            self.volume_slider = Slider(pos=slider_placeholder.absolute_pos, size=slider_placeholder.size,
                                        initial_val=settings_manager.SETTINGS.get("master_volume", 0.5),
                                        on_value_changed=self.on_volume_change)

        # --- Keybinds ---
        self.keybind_buttons = {}
        self.keybind_labels = {}
        self.is_rebinding = False
        self.rebinding_lane = None
        for i in range(4):  # Assuming 4 keys
            btn = self.ui_manager.get_element_by_name(f"keybind_{i}_button")
            if isinstance(btn, Button):
                btn.on_click = lambda i=i: self.start_rebinding(i)
                self.keybind_buttons[i] = btn
                # Create a text label to sit inside the button
                label = Label(name=f"keybind_{i}_label", pos=(0, 0), size=btn.size, parent=btn)
                label.set_text(settings_manager.get_keybinds().get(str(i), "").upper())
                label.align = "center"
                label.create_text_surface()
                self.keybind_labels[i] = label

    def toggle(self):
        if self.is_animating: return
        self.is_active = not self.is_active
        self.is_animating = True
        target_pos = self.on_screen_pos if self.is_active else self.off_screen_pos
        if self.settings_panel:
            self.settings_panel.animate_position(target_pos, 0.5)
        if self.is_active:
            self.update_keybind_labels()  # Refresh labels when opening
        else:
            settings_manager.save_settings()

    def on_volume_change(self, new_volume):
        settings_manager.set_volume(new_volume)

    def start_rebinding(self, lane_index):
        if self.is_rebinding: return
        self.is_rebinding = True
        self.rebinding_lane = lane_index
        # Visually indicate which key is being changed
        for i, label in self.keybind_labels.items():
            if i == lane_index:
                label.set_text("...")
            else:  # Dim other buttons
                label.color = (100, 100, 100, 255)
                label.create_text_surface()

    def finish_rebinding(self, key_name):
        settings_manager.set_keybind(self.rebinding_lane, key_name)
        self.is_rebinding = False
        self.rebinding_lane = None
        self.update_keybind_labels()

    def update_keybind_labels(self):
        keybinds = settings_manager.get_keybinds()
        for i, label in self.keybind_labels.items():
            label.color = (255, 255, 255, 255)
            label.set_text(keybinds.get(str(i), "").upper())

    def get_event(self, event):
        if not self.is_active: return

        if self.is_rebinding:
            if event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:  # Allow escape to cancel
                    self.finish_rebinding(pygame.key.name(event.key))
                else:  # Cancel rebinding
                    self.is_rebinding = False
                    self.update_keybind_labels()
            return  # Block other input while rebinding

        if self.volume_slider: self.volume_slider.get_event(event)
        self.ui_manager.get_event(event)

    def update(self, dt):
        if not self.settings_panel: return
        self.ui_manager.update(dt)
        if self.volume_slider:
            slider_placeholder = self.ui_manager.get_element_by_name("volume_slider_placeholder")
            if slider_placeholder:
                self.volume_slider.rect.topleft = slider_placeholder.absolute_pos
                self.volume_slider._update_handle_pos()
        if self.is_animating and not self.settings_panel.is_animating:
            self.is_animating = False

    def draw(self, surface):
        if not self.is_active and not self.is_animating: return

        pos_x = self.settings_panel.absolute_pos[0]
        on_x, off_x = self.on_screen_pos[0], self.off_screen_pos[0]
        progress = (pos_x - off_x) / (on_x - off_x) if (on_x - off_x) != 0 else 0
        overlay_alpha = int(180 * progress)
        if overlay_alpha > 0:
            overlay = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, max(0, overlay_alpha)))
            surface.blit(overlay, (0, 0))

        self.ui_manager.draw(surface)
        if self.volume_slider: self.volume_slider.draw(surface)

