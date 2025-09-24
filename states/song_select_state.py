import pygame
import os
import json
from settings import *
from states.base_state import BaseState
from ui.ui_manager import UIManager
from ui.image_panel import ImagePanel
from ui.label import Label
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
        self.background_img = pygame.Surface(self.screen_rect.size)
        self.background_img.fill(BLACK)

        self.target_scroll_y = 0
        self.current_scroll_y = 0

        self.scan_for_songs()
        self.load_all_song_assets()

        if self.songs:
            self.select_song(0, instant=True)

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
        banner_size = self.banner_placeholder.size if self.banner_placeholder else (740, 70)
        for i in range(len(self.songs)):
            if self.songs[i]["image_path"]:
                original_image = asset_loader.load_image(self.songs[i]["image_path"])
                self.songs[i]["original_img"] = original_image
                if original_image:
                    self.songs[i]["banner_img"] = asset_loader.scale_to_cover(original_image, banner_size)
                    self.songs[i]["accent_color"] = asset_loader.get_dominant_color(original_image, vibrant=True)
                else:
                    self.songs[i]["banner_img"], self.songs[i]["accent_color"] = None, DEFAULT_ACCENT_COLOR
            else:
                self.songs[i]["original_img"], self.songs[i]["banner_img"], self.songs[i][
                    "accent_color"] = None, None, DEFAULT_ACCENT_COLOR

    def select_song(self, index, instant=False):
        if not self.songs or not (0 <= index < len(self.songs)): return

        self.selected_index = index
        song_data = self.songs[index]

        banner_h_margin = 80
        self.target_scroll_y = self.screen_rect.centery - (self.selected_index * banner_h_margin)
        if instant:
            self.current_scroll_y = self.target_scroll_y

        if song_data.get("original_img"):
            self.background_img = asset_loader.create_blurred_background(song_data["original_img"],
                                                                         self.screen_rect.size)
        else:
            self.background_img.fill(BLACK)

        # --- FIX: Use the correct, case-sensitive names from your Figma design ---
        ui_text_map = {
            "Beatmaps_Name": song_data["title"],
            "Beatmapper_Name": song_data["artist"],
            "beatmap_bpm": str(song_data["bpm"]),
            "beatmap_length": str(song_data["length"]),
            "beatmap_notes_amount": str(song_data["notes"]),
        }
        for name, text in ui_text_map.items():
            element = self.ui_manager.get_element_by_name(name)
            if element and hasattr(element, 'set_text'): element.set_text(text)

        # --- FIX: Look for the placeholder with the required "IMG_" prefix ---
        # In Figma/JSON, the layer must be named "IMG_beatmap_art_placeholder"
        artwork_placeholder = self.ui_manager.get_element_by_name("IMG_beatmap_art_placeholder")
        if artwork_placeholder and isinstance(artwork_placeholder, ImagePanel):
            artwork_placeholder.set_image(song_data.get("original_img"))

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
                    self.select_song((self.selected_index + 1) % len(self.songs))
                elif event.key == pygame.K_UP:
                    self.select_song((self.selected_index - 1 + len(self.songs)) % len(self.songs))
                elif event.key == pygame.K_RETURN:
                    self.persist["selected_song_data"] = self.songs[self.selected_index]
                    self.persist["final_background"] = self.background_img
                    pygame.mixer.music.fadeout(500)
                    self.go_to_next_state()

    def update(self, dt):
        super().update(dt)
        self.ui_manager.update(dt)
        scroll_speed = 10
        self.current_scroll_y += (self.target_scroll_y - self.current_scroll_y) * scroll_speed * (dt / 1000.0)

    def draw(self, surface):
        surface.blit(self.background_img, (0, 0))
        self.ui_manager.draw(surface)
        self.draw_song_list(surface)

    def draw_song_list(self, surface):
        if not self.songs or not self.banner_placeholder: return

        list_x = self.banner_placeholder.absolute_pos[0]
        banner_h_margin = 80

        for i, song in enumerate(self.songs):
            y_pos = self.current_scroll_y + (i * banner_h_margin) - (banner_h_margin / 2)

            if y_pos > self.screen_rect.height or y_pos < -banner_h_margin:
                continue

            banner_rect = pygame.Rect(list_x, y_pos, self.banner_placeholder.size[0], self.banner_placeholder.size[1])

            if song.get("banner_img"):
                clip_surface = pygame.Surface(banner_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(clip_surface, WHITE, (0, 0, *banner_rect.size), border_radius=10)
                clip_surface.blit(song["banner_img"], (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                surface.blit(clip_surface, banner_rect.topleft)
            else:
                pygame.draw.rect(surface, (30, 30, 30), banner_rect, border_radius=10)

            overlay = pygame.Surface(banner_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 150), (0, 0, *banner_rect.size), border_radius=10)
            surface.blit(overlay, banner_rect.topleft)

            draw_text(surface, song["title"], (banner_rect.x + 20, banner_rect.centery - 10),
                      self.font_banner_title, WHITE, text_rect_origin='topleft')
            draw_text(surface, song["artist"], (banner_rect.x + 20, banner_rect.centery + 12),
                      self.font_banner_artist, (200, 200, 200), text_rect_origin='topleft')

            if i == self.selected_index:
                pygame.draw.rect(surface, song["accent_color"], banner_rect, 3, border_radius=10)

