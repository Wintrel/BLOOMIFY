import pygame
import os
import json
import math
import time
from settings import *
from states.base_state import BaseState
from ui.ui_manager import UIManager
from ui.image_panel import ImagePanel
from utils import draw_text
import asset_loader


class SongSelectState(BaseState):
    def __init__(self, state_manager):
        super(SongSelectState, self).__init__(state_manager)
        self.next_state = "LOADING"
        self.ui_manager = UIManager()
        self.ui_manager.load_layout("layouts/Song_Select_Layout.json")
        self.banner_placeholder = self.ui_manager.get_element_by_name("song_banner")
        if self.banner_placeholder:
            self.banner_placeholder.visible = False
        self.font_banner_title = asset_loader.load_font("Inter", 22)
        self.font_banner_artist = asset_loader.load_font("Inter", 16)
        self.songs = []
        self.selected_index = 0

        # --- Scrolling and Banner Animation ---
        self.target_scroll_y = 0
        self.current_scroll_y = 0

        # --- Enhanced Background & Artwork Transition ---
        self.current_background = pygame.Surface(self.screen_rect.size)
        self.current_background.fill(BLACK)
        self.pending_background = None
        self.pending_artwork = None
        self.background_fade_alpha = 0
        self.background_change_timer = 0
        self.background_change_delay = 0.3  # 300ms delay
        self.background_fade_duration = 0.4  # 400ms fade

        self.scan_for_songs()
        self.load_all_song_assets()

    def startup(self, persistent):
        super().startup(persistent)
        menu_music_was_playing = self.persist.get('menu_music_active', False)
        song_to_select_index = 0

        if menu_music_was_playing:
            menu_beatmap_path = self.persist.get('menu_music_beatmap_path')
            if menu_beatmap_path:
                for i, song in enumerate(self.songs):
                    if os.path.normpath(song['beatmap_path']) == os.path.normpath(menu_beatmap_path):
                        song_to_select_index = i
                        break

        if self.songs:
            # This single call now handles instantly setting the background, artwork, and music
            self.select_song(song_to_select_index, instant=True, play_preview=not menu_music_was_playing)

    def scan_for_songs(self):
        songs_path = "assets/beatmaps"
        if not os.path.exists(songs_path): return
        for folder_name in os.listdir(songs_path):
            folder_path = os.path.join(songs_path, folder_name)
            if os.path.isdir(folder_path):
                beatmap_path = os.path.join(folder_path, "beatmap.json")
                if os.path.exists(beatmap_path):
                    try:
                        with open(beatmap_path, 'r', encoding='utf-8') as f:
                            beatmap_data = json.load(f)
                        image_file = next(
                            (f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))), None)
                        song_entry = {
                            "title": beatmap_data.get("title", "N/A"), "artist": beatmap_data.get("artist", "N/A"),
                            "bpm": beatmap_data.get("bpm", "N/A"), "length": beatmap_data.get("length", "N/A"),
                            "notes": len(beatmap_data.get("notes", [])), "beatmap_path": beatmap_path,
                            "audio_path": os.path.join(folder_path, beatmap_data.get("audio_path", "")),
                            "image_path": os.path.join(folder_path, image_file) if image_file else None,
                            "preview_time_ms": beatmap_data.get("preview_time_ms", 0)
                        }
                        self.songs.append(song_entry)
                    except Exception as e:
                        print(f"Error loading song {folder_name}: {e}")

    def load_all_song_assets(self):
        if not self.banner_placeholder: return
        banner_size = self.banner_placeholder.size
        banner_w, banner_h = banner_size
        for song in self.songs:
            original_image = asset_loader.load_image(song["image_path"]) if song.get("image_path") else None
            song["original_img"] = original_image
            banner_img = None
            if original_image:
                banner_img = asset_loader.scale_to_cover(original_image, banner_size)
                accent_color = asset_loader.get_dominant_color(original_image, vibrant=True)
            else:
                accent_color = DEFAULT_ACCENT_COLOR
            song["accent_color"] = accent_color
            banner_surface = pygame.Surface(banner_size, pygame.SRCALPHA)
            if banner_img:
                clip_surface = pygame.Surface(banner_size, pygame.SRCALPHA)
                pygame.draw.rect(clip_surface, WHITE, (0, 0, *banner_size), border_radius=10)
                clip_surface.blit(banner_img, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                banner_surface.blit(clip_surface, (0, 0))
            else:
                pygame.draw.rect(banner_surface, (30, 30, 30), (0, 0, *banner_size), border_radius=10)
            overlay = pygame.Surface(banner_size, pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 150), (0, 0, *banner_size), border_radius=10)
            banner_surface.blit(overlay, (0, 0))
            draw_text(banner_surface, song["title"], (20, banner_h / 2 - 10), self.font_banner_title, WHITE,
                      text_rect_origin='midleft')
            draw_text(banner_surface, song["artist"], (20, banner_h / 2 + 12), self.font_banner_artist, (200, 200, 200),
                      text_rect_origin='midleft')
            song["banner_surface"] = banner_surface
            selected_banner_surface = banner_surface.copy()
            pygame.draw.rect(selected_banner_surface, accent_color, (0, 0, *banner_size), 3, border_radius=10)
            song["selected_banner_surface"] = selected_banner_surface

    def select_song(self, index, instant=False, play_preview=True):
        if not self.songs or not (0 <= index < len(self.songs)): return
        self.selected_index = index
        song_data = self.songs[index]
        banner_h_margin = 80
        self.target_scroll_y = self.screen_rect.centery - (self.selected_index * banner_h_margin)
        if instant: self.current_scroll_y = self.target_scroll_y

        # Update text labels (these should always be instant)
        ui_text_map = {
            "Beatmaps_name": song_data["title"], "Beatmapper_Name": song_data["artist"],
            "beatmap_bpm": str(song_data["bpm"]), "beatmap_length": str(song_data["length"]),
            "beatmap_notes_amount": str(song_data["notes"]),
        }
        for name, text in ui_text_map.items():
            element = self.ui_manager.get_element_by_name(name)
            if element and hasattr(element, 'set_text'): element.set_text(text)

        artwork_placeholder = self.ui_manager.get_element_by_name("IMG_beatmap_art_placeholder")

        # --- Handle visual transitions ---
        if instant:
            # Instantly set background and artwork
            if song_data.get("original_img"):
                self.current_background = asset_loader.create_blurred_background(song_data["original_img"],
                                                                                 self.screen_rect.size)
                if artwork_placeholder and isinstance(artwork_placeholder, ImagePanel):
                    artwork_placeholder.set_image(song_data.get("original_img"))
            else:
                self.current_background.fill(BLACK)
                if artwork_placeholder and isinstance(artwork_placeholder, ImagePanel):
                    artwork_placeholder.set_image(None)
        else:
            # Trigger the delayed change for background and artwork
            if song_data.get("original_img"):
                self.pending_background = asset_loader.create_blurred_background(song_data["original_img"],
                                                                                 self.screen_rect.size)
                self.pending_artwork = song_data.get("original_img")
            else:
                self.pending_background = pygame.Surface(self.screen_rect.size)
                self.pending_background.fill(BLACK)
                self.pending_artwork = None

            self.background_change_timer = time.time()
            self.background_fade_alpha = 0

        if play_preview:
            audio_path = song_data["audio_path"]
            if os.path.exists(audio_path):
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play(start=song_data["preview_time_ms"] / 1000.0)
            else:
                pygame.mixer.music.stop()

    def get_event(self, event):
        super().get_event(event)
        if self.transition_state == "static" and self.songs:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.select_song((self.selected_index + 1) % len(self.songs), play_preview=True)
                elif event.key == pygame.K_UP:
                    self.select_song((self.selected_index - 1 + len(self.songs)) % len(self.songs), play_preview=True)
                elif event.key == pygame.K_RETURN:
                    self.persist['menu_music_active'] = False
                    self.persist["selected_song_data"] = self.songs[self.selected_index]
                    self.persist["final_background"] = self.current_background
                    pygame.mixer.music.fadeout(500)
                    self.go_to_next_state()

    def update(self, dt):
        super().update(dt)
        self.ui_manager.update(dt)
        scroll_speed_factor = 1.0 - math.exp(-15 * (dt / 1000.0))
        self.current_scroll_y += (self.target_scroll_y - self.current_scroll_y) * scroll_speed_factor

        # --- Update background transition ---
        if self.pending_background and time.time() > self.background_change_timer + self.background_change_delay:
            fade_increment = (255 / self.background_fade_duration) * (dt / 1000.0)
            self.background_fade_alpha += fade_increment
            if self.background_fade_alpha >= 255:
                self.background_fade_alpha = 255
                self.current_background = self.pending_background
                self.pending_background = None

                # --- Update the artwork panel now that the fade is complete ---
                artwork_placeholder = self.ui_manager.get_element_by_name("IMG_beatmap_art_placeholder")
                if artwork_placeholder and isinstance(artwork_placeholder, ImagePanel):
                    artwork_placeholder.set_image(self.pending_artwork)
                self.pending_artwork = None

    def draw(self, surface):
        # --- Draw current background ---
        surface.blit(self.current_background, (0, 0))

        # --- Draw fading pending background ---
        if self.pending_background and self.background_fade_alpha > 0:
            self.pending_background.set_alpha(int(self.background_fade_alpha))
            surface.blit(self.pending_background, (0, 0))

        self.ui_manager.draw(surface)
        self.draw_song_list(surface)

    def draw_song_list(self, surface):
        if not self.songs or not self.banner_placeholder: return
        list_x = self.banner_placeholder.absolute_pos[0]
        banner_w, banner_h = self.banner_placeholder.size
        banner_h_margin = 80
        for i, song in enumerate(self.songs):
            y_pos = self.current_scroll_y + (i * banner_h_margin) - (banner_h_margin / 2)
            if y_pos > self.screen_rect.height or y_pos + banner_h < 0: continue
            if i == self.selected_index:
                surface.blit(song["selected_banner_surface"], (list_x, y_pos))
            else:
                surface.blit(song["banner_surface"], (list_x, y_pos))

