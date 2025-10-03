import pygame
import os
import random
import json
import math
from settings import *
from states.base_state import BaseState
from ui.ui_manager import UIManager
from utils import draw_text
import asset_loader


class MainMenuState(BaseState):
    def __init__(self, state_manager):
        super(MainMenuState, self).__init__(state_manager)
        self.next_state = "SONG_SELECT"
        self.ui_manager = UIManager()
        self.ui_manager.load_layout("layouts/Main_Menu_Layout.json")
        self.is_transitioning_out = False
        self.transition_anim_duration = 0.5

        # --- Hold to Quit ---
        self.esc_hold_time = 0.0
        self.quit_hold_duration = 1.5  # Longer for a better effect
        self.is_quitting = False
        self.font_quit = asset_loader.load_font("Inter", 30)

    def startup(self, persistent):
        super().startup(persistent)
        # Reset state
        self.is_transitioning_out = False
        self.esc_hold_time = 0.0
        self.is_quitting = False

        # If menu music is not already playing, start it
        if not self.persist.get('menu_music_active', False) or not pygame.mixer.music.get_busy():
            self.start_menu_music()

        self.trigger_transition_in()

    def start_menu_music(self):
        songs_path = "assets/beatmaps"  # Corrected path to be consistent
        if not os.path.exists(songs_path): return

        all_beatmap_paths = []
        for folder_name in os.listdir(songs_path):
            folder_path = os.path.join(songs_path, folder_name)
            if os.path.isdir(folder_path):
                beatmap_path = os.path.join(folder_path, "beatmap.json")
                if os.path.exists(beatmap_path):
                    all_beatmap_paths.append((folder_path, beatmap_path))

        if all_beatmap_paths:
            random_song_folder, beatmap_path = random.choice(all_beatmap_paths)
            try:
                with open(beatmap_path, 'r', encoding='utf-8') as f:
                    beatmap_data = json.load(f)  # Use json.load for robustness

                audio_filename = beatmap_data.get("audio_path")
                if audio_filename:
                    audio_path = os.path.join(random_song_folder, audio_filename)
                    if os.path.exists(audio_path):
                        pygame.mixer.music.load(audio_path)
                        pygame.mixer.music.play(-1)
                        self.persist['menu_music_active'] = True
                        self.persist['menu_music_beatmap_path'] = beatmap_path
            except Exception as e:
                print(f"Error starting menu music from {beatmap_path}: {e}")

    def trigger_transition_in(self):
        """ Animates UI elements onto the screen when returning to this state. """
        title = self.ui_manager.get_element_by_name("game_name")
        if title: title.animate_position(title.pos, self.transition_anim_duration)
        subtitle = self.ui_manager.get_element_by_name("game_desc")
        if subtitle: subtitle.animate_position(subtitle.pos, self.transition_anim_duration)
        prompt = self.ui_manager.get_element_by_name("click_prompt")
        if prompt: prompt.animate_position(prompt.pos, self.transition_anim_duration)

    def get_event(self, event):
        super().get_event(event)
        if not self.is_transitioning_out and self.transition_state == "static" and not self.is_quitting:
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                self.trigger_transition_out()

    def trigger_transition_out(self):
        self.is_transitioning_out = True
        self.go_to_next_state()
        title = self.ui_manager.get_element_by_name("game_name")
        if title: title.animate_position((title.absolute_pos[0], -title.size[1]), self.transition_anim_duration)
        subtitle = self.ui_manager.get_element_by_name("game_desc")
        if subtitle: subtitle.animate_position((subtitle.absolute_pos[0], self.screen_rect.height),
                                               self.transition_anim_duration)
        prompt = self.ui_manager.get_element_by_name("click_prompt")
        if prompt: prompt.animate_position((prompt.absolute_pos[0], self.screen_rect.height),
                                           self.transition_anim_duration)

    def update(self, dt):
        super().update(dt)
        self.ui_manager.update(dt)

        # --- Hold to Quit Logic ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] and not self.is_transitioning_out:
            self.is_quitting = True
            self.esc_hold_time += dt / 1000.0
            if self.esc_hold_time >= self.quit_hold_duration:
                self.quit = True
        else:
            # Reset if ESC is released
            self.is_quitting = False
            self.esc_hold_time = 0.0

    def draw(self, surface):
        surface.fill(BLACK)

        progress = self.esc_hold_time / self.quit_hold_duration

        # The UI is drawn first. If we are deep into the quit animation, we skip drawing it to make it "vanish".
        if not self.is_quitting or progress < 0.3:
            self.ui_manager.draw(surface)

        # --- Draw Hold to Quit Glitch Animation ---
        if self.is_quitting:
            # 1. Horizontal slice shifting effect
            num_shifts = int(progress * 20)
            for _ in range(num_shifts):
                h = random.randint(2, 20)
                y = random.randint(0, self.screen_rect.height - h)
                try:
                    # Grab a slice of the screen to shift
                    subsurface = surface.subsurface(pygame.Rect(0, y, self.screen_rect.width, h)).copy()
                    shift_amount = random.randint(-int(progress * 60), int(progress * 60))
                    surface.blit(subsurface, (shift_amount, y))
                except ValueError:
                    continue  # Skip if slice is out of bounds

            # 2. Chromatic aberration effect (color splitting)
            if progress > 0.2:
                temp_surface = surface.copy()
                red_surface = temp_surface.copy();
                red_surface.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
                cyan_surface = temp_surface.copy();
                cyan_surface.fill((0, 255, 255), special_flags=pygame.BLEND_RGB_MULT)

                offset = int(progress * 15)
                surface.blit(red_surface, (random.randint(-offset, offset), random.randint(-offset, offset)),
                             special_flags=pygame.BLEND_RGB_ADD)
                surface.blit(cyan_surface, (random.randint(-offset, offset), random.randint(-offset, offset)),
                             special_flags=pygame.BLEND_RGB_ADD)

            # 3. Draw "QUITTING..." text that fades in
            if progress > 0.5:
                text_alpha = min(255, int((progress - 0.5) * 2 * 255))
                draw_text(surface, "QUITTING...", self.screen_rect.center,
                          self.font_quit, (255, 255, 255, text_alpha), text_rect_origin='center')

