import pygame
from settings import *
from ui.ui_manager import UIManager
from ui.custom_widgets.slider import Slider
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

        self.volume_slider = None
        self.slider_placeholder = self.ui_manager.get_element_by_name("volume_slider_placeholder")
        if self.slider_placeholder:
            self.volume_slider = Slider(
                pos=self.slider_placeholder.absolute_pos,
                size=self.slider_placeholder.size,
                initial_val=settings_manager.SETTINGS.get("master_volume", 0.5),
                on_value_changed=self.on_volume_change
            )

    def toggle(self):
        if self.is_animating: return

        self.is_active = not self.is_active
        self.is_animating = True

        target_pos = self.on_screen_pos if self.is_active else self.off_screen_pos
        if self.settings_panel:
            self.settings_panel.animate_position(target_pos, 0.5)

        if not self.is_active:
            settings_manager.save_settings()

    def on_volume_change(self, new_volume):
        settings_manager.set_volume(new_volume)

    def get_event(self, event):
        # Only process events if the menu is at least partially on-screen
        if self.settings_panel and self.settings_panel.absolute_pos[0] < SCREEN_WIDTH:
            if self.volume_slider:
                self.volume_slider.get_event(event)

    def update(self, dt):
        if not self.settings_panel: return

        self.ui_manager.update(dt)

        if self.volume_slider and self.slider_placeholder:
            self.volume_slider.rect.topleft = self.slider_placeholder.absolute_pos
            self.volume_slider._update_handle_pos()

        if self.is_animating and not self.settings_panel.is_animating:
            self.is_animating = False

    def draw(self, surface):
        # If the panel is completely off-screen, don't draw anything
        if not self.settings_panel or (not self.is_active and not self.is_animating):
            return

        # --- FIX: Synchronized Overlay Fade ---
        # Calculate the overlay's transparency based on the panel's animation progress.
        pos_x = self.settings_panel.absolute_pos[0]
        on_x = self.on_screen_pos[0]
        off_x = self.off_screen_pos[0]

        overlay_alpha = 0
        if (on_x - off_x) != 0:
            progress = (pos_x - off_x) / (on_x - off_x)
            overlay_alpha = int(180 * progress)

        if overlay_alpha > 0:
            overlay = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, max(0, overlay_alpha)))
            surface.blit(overlay, (0, 0))

        self.ui_manager.draw(surface)
        if self.volume_slider:
            self.volume_slider.draw(surface)

