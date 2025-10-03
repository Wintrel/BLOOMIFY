import pygame
import os
import json
import time
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

        # --- UI & Layout ---
        self.ui_manager = UIManager()
        self.ui_manager.load_layout("layouts/Song_Select_Layout.json")

        self.banner_placeholder = self.ui_manager.get_element_by_name("song_banner")
        if self.banner_placeholder:
            self.banner_placeholder.visible = False

        # --- fonts ---
        self.font_banner_title = asset_loader.load_font("Inter", 22)
        self.font_banner_artist = asset_loader.load_font("Inter", 16)

        # --- Song Data ---
        self.songs = []
        self.selected_index = 0

        # --- Smooth Scrolling ---
        self.target_scroll_y = 0
        self.current_scroll_y = 0
        self.scroll_smoothness = 4.0  # Higher is snappier

        # --- Enhanced Background & Artwork Transition (from old state) ---
        self.current_background = pygame.Surface(self.screen_rect.size)
        self.current_background.fill(BLACK)
        self.pending_background = None
        self.pending_artwork = None
        self.background_fade_alpha = 0
        self.background_change_timer = 0
        self.background_change_delay = 0.3  # 300ms delay
        self.background_fade_duration = 0.4  # 400ms fade

        # --- State Flags ---
        self.menu_music_was_playing = False
        self.is_transitioning_out = False

        self.scan_for_songs()
        self.load_all_song_assets()

        if self.songs:
            self.select_song(0, instant=True, play_preview=False)

    def startup(self, persistent):
        super().startup(persistent)
        self.is_transitioning_out = False
        self.menu_music_was_playing = self.persist.get('menu_music_active', False)

        song_to_select_index = 0
        if self.menu_music_was_playing:
            menu_beatmap_path = self.persist.get('menu_music_beatmap_path')
            if menu_beatmap_path:
                for i, song in enumerate(self.songs):
                    if song['beatmap_path'] == menu_beatmap_path:
                        song_to_select_index = i
                        break

        if self.songs:
            self.select_song(song_to_select_index, instant=True, play_preview=not self.menu_music_was_playing)

        self.trigger_transition_in()

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
                            data = json.load(f)
                        img_file = next(
                            (f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))), None)
                        self.songs.append({
                            "title": data.get("title", folder_name),
                            "artist": data.get("artist", "Unknown Artist"),
                            "bpm": data.get("bpm", "N/A"),
                            "length": data.get("length", "N/A"),
                            "notes": len(data.get("notes", [])),
                            "beatmap_path": beatmap_path,
                            "audio_path": os.path.join(folder_path, data.get("audio_path", "")),
                            "image_path": os.path.join(folder_path, img_file) if img_file else None,
                            "preview_time_ms": data.get("preview_time_ms", 0)
                        })
                    except Exception as e:
                        print(f"Error loading song data in '{folder_name}': {e}")

    def load_all_song_assets(self):
        banner_size = self.banner_placeholder.size if self.banner_placeholder else (740, 70)
        for i in range(len(self.songs)):
            if self.songs[i]["image_path"]:
                img = asset_loader.load_image(self.songs[i]["image_path"])
                self.songs[i]["original_img"] = img
                if img:
                    self.songs[i]["banner_img"] = asset_loader.scale_to_cover(img, banner_size)
                    self.songs[i]["accent_color"] = asset_loader.get_dominant_color(img, vibrant=True)
                else:
                    self.songs[i]["banner_img"], self.songs[i]["accent_color"] = None, DEFAULT_ACCENT_COLOR
            else:
                self.songs[i]["original_img"], self.songs[i]["banner_img"], self.songs[i][
                    "accent_color"] = None, None, DEFAULT_ACCENT_COLOR

    def select_song(self, index, instant=False, play_preview=True):
        if not self.songs or not (0 <= index < len(self.songs)): return
        self.selected_index = index
        song_data = self.songs[index]

        banner_h_margin = 80
        self.target_scroll_y = self.screen_rect.centery - (self.selected_index * banner_h_margin)
        if instant:
            self.current_scroll_y = self.target_scroll_y

        ui_text_map = {
            "Beatmaps_name": song_data["title"], "Beatmapper_Name": song_data["artist"],
            "beatmap_bpm": str(song_data["bpm"]), "beatmap_length": str(song_data["length"]),
            "beatmap_notes_amount": str(song_data["notes"]),
        }
        for name, text in ui_text_map.items():
            element = self.ui_manager.get_element_by_name(name)
            if element and hasattr(element, 'set_text'): element.set_text(text)

        artwork_placeholder = self.ui_manager.get_element_by_name("IMG_beatmap_art_placeholder")

        # --- Handle visual transitions (from old state) ---
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
        if self.transition_state == "static" and self.songs and not self.is_transitioning_out:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.next_state = "MAIN_MENU"
                    self.trigger_transition_out()
                    pygame.mixer.music.fadeout(500)
                    return

                play_preview = True
                if self.menu_music_was_playing:
                    self.menu_music_was_playing = False
                    self.persist['menu_music_active'] = False
                    play_preview = False

                if event.key == pygame.K_DOWN:
                    self.select_song((self.selected_index + 1) % len(self.songs), play_preview=play_preview)
                elif event.key == pygame.K_UP:
                    self.select_song((self.selected_index - 1 + len(self.songs)) % len(self.songs),
                                     play_preview=play_preview)
                elif event.key == pygame.K_RETURN:
                    self.next_state = 'LOADING'
                    self.persist['menu_music_active'] = False
                    self.persist["selected_song_data"] = self.songs[self.selected_index]
                    self.persist["final_background"] = self.current_background  # Use current_background
                    pygame.mixer.music.fadeout(500)
                    self.trigger_transition_out()

    def update(self, dt):
        super().update(dt)
        self.ui_manager.update(dt)

        # Update smooth scrolling
        diff = self.target_scroll_y - self.current_scroll_y
        self.current_scroll_y += diff * min(1, self.scroll_smoothness * (dt / 1000.0))

        # --- Update background transition (from old state) ---
        if self.pending_background and time.time() > self.background_change_timer + self.background_change_delay:
            fade_increment = (255 / self.background_fade_duration) * (dt / 1000.0)
            self.background_fade_alpha += fade_increment
            if self.background_fade_alpha >= 255:
                self.background_fade_alpha = 255
                self.current_background = self.pending_background
                self.pending_background = None

                # Update the artwork panel now that the fade is complete
                artwork_placeholder = self.ui_manager.get_element_by_name("IMG_beatmap_art_placeholder")
                if artwork_placeholder and isinstance(artwork_placeholder, ImagePanel):
                    artwork_placeholder.set_image(self.pending_artwork)
                self.pending_artwork = None

    def draw(self, surface):
        # --- Draw current background (from old state) ---
        surface.blit(self.current_background, (0, 0))

        # --- Draw fading pending background (from old state) ---
        if self.pending_background and self.background_fade_alpha > 0:
            self.pending_background.set_alpha(int(self.background_fade_alpha))
            surface.blit(self.pending_background, (0, 0))

        self.ui_manager.draw(surface)
        self.draw_song_list(surface)

    def draw_song_list(self, surface):
        if not self.songs or not self.banner_placeholder: return
        list_x = self.banner_placeholder.absolute_pos[0]
        banner_h_margin = 80
        for i, song in enumerate(self.songs):
            y_pos = self.current_scroll_y + (i * banner_h_margin) - (banner_h_margin / 2)
            if y_pos > self.screen_rect.height or y_pos < -banner_h_margin: continue
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

    # --- Transition animation methods from previous implementation ---
    def trigger_transition_in(self):
        duration = 0.6
        info_panel = self.ui_manager.get_element_by_name("info_panel")
        if info_panel:
            target_x = info_panel.pos[0]
            info_panel.absolute_pos[0] = -info_panel.size[0]
            info_panel.animate_position((target_x, info_panel.absolute_pos[1]), duration)
        if self.banner_placeholder:
            target_x = self.banner_placeholder.pos[0]
            self.banner_placeholder.absolute_pos[0] = self.screen_rect.width
            self.banner_placeholder.animate_position((target_x, self.banner_placeholder.absolute_pos[1]), duration)

    def trigger_transition_out(self):
        self.is_transitioning_out = True
        self.go_to_next_state()
        duration = 0.5
        info_panel = self.ui_manager.get_element_by_name("info_panel")
        if info_panel:
            info_panel.animate_position((-info_panel.size[0], info_panel.absolute_pos[1]), duration)
        if self.banner_placeholder:
            self.banner_placeholder.animate_position((self.screen_rect.width, self.banner_placeholder.absolute_pos[1]),
                                                     duration)
