import pygame
import os
import json
import math
from settings import *
from .base import BaseState
from .utility import draw_text, get_dominant_color, scale_to_cover


# noinspection D
class SongSelect(BaseState):
    def __init__(self):
        super(SongSelect, self).__init__()
        self.next_state = "LOADING"
        self.accent_color = DEFAULT_ACCENT_COLOR

        # --- Load Fonts ---
        self.font_title = pygame.font.Font(None, 42)
        self.font_artist = pygame.font.Font(None, 24)
        self.font_stats_label = pygame.font.Font(None, 16)
        self.font_stats_value = pygame.font.Font(None, 20)
        self.font_banner_title = pygame.font.Font(None, 22)
        self.font_banner_artist = pygame.font.Font(None, 16)
        self.font_header = pygame.font.Font(None, 18)

        # --- Song Data ---
        self.songs = []
        self.selected_index = 0
        self.scan_for_songs()

        if self.songs:
            self.load_song_assets()
            self.select_song(0)
        else:
            self.selected_song = {"title": "No Songs Found", "artist": "Please add songs to assets/songs", "bpm": "N/A",
                                  "length": "N/A", "notes": 0}
            self.background_img = pygame.Surface(self.screen_rect.size)
            self.background_img.fill(BLACK)

    def startup(self, persistent):
        """ When returning to this state, start the music preview again. """
        super().startup(persistent)
        if self.songs:
            self.play_song_preview()

    def ease_out_cubic(self, x):
        return 1 - pow(1 - x, 3)

    def scan_for_songs(self):
        songs_path = "assets/songs"
        if not os.path.exists(songs_path): return

        for folder_name in os.listdir(songs_path):
            folder_path = os.path.join(songs_path, folder_name)
            if os.path.isdir(folder_path):
                beatmap_path = os.path.join(folder_path, "beatmap.json")
                if os.path.exists(beatmap_path):
                    try:
                        with open(beatmap_path, 'r') as f:
                            beatmap_data = json.load(f)

                        image_files = os.listdir(folder_path)
                        blurred_image_file = next((f for f in image_files if
                                                   "blurred" in f.lower() and f.lower().endswith(
                                                       ('.png', '.jpg', '.jpeg'))), None)
                        regular_image_file = next((f for f in image_files if
                                                   "blurred" not in f.lower() and f.lower().endswith(
                                                       ('.png', '.jpg', '.jpeg'))), None)


                        audio_filename = beatmap_data.get("audio_path")

                        song_entry = {
                            "title": beatmap_data.get("title", "Unknown Title"),
                            "artist": beatmap_data.get("artist", "Unknown Artist"),
                            "bpm": beatmap_data.get("bpm", "N/A"),
                            "length": beatmap_data.get("length", "N/A"),
                            "notes": len(beatmap_data.get("notes", [])),
                            "beatmap_path": beatmap_path,
                            "image_path": os.path.join(folder_path, regular_image_file) if regular_image_file else None,
                            "blurred_image_path": os.path.join(folder_path,
                                                               blurred_image_file) if blurred_image_file else None,
                            "audio_path": os.path.join(folder_path, audio_filename) if audio_filename else None,
                            "preview_time_ms": beatmap_data.get("preview_time_ms", 10000)  # Default to 10s
                        }
                        self.songs.append(song_entry)
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Error loading beatmap data from '{folder_name}': {e}")

    def _create_fallback_blur(self, image):
        small_size = (self.screen_rect.width // 10, self.screen_rect.height // 10)
        large_size = self.screen_rect.size
        scaled_down = pygame.transform.smoothscale(image, small_size)
        blurred = pygame.transform.smoothscale(scaled_down, large_size)
        blurred.fill((0, 0, 0, 150), special_flags=pygame.BLEND_RGBA_SUB)
        return blurred

    def _vibrant_color(self, color):
        try:
            h, s, v, a = pygame.Color(*color).hsva
            s = max(s, 70);
            v = max(v, 80)
            vibrant = pygame.Color(0);
            vibrant.hsva = (h, s, v, a)
            return (vibrant.r, vibrant.g, vibrant.b)
        except (ValueError, TypeError):
            return DEFAULT_ACCENT_COLOR

    def load_song_assets(self):
        banner_size = (450, 90)
        for i, song in enumerate(self.songs):
            if song["image_path"] and os.path.exists(song["image_path"]):
                try:
                    original_image = pygame.image.load(song["image_path"]).convert_alpha()
                    self.songs[i]["banner_img"] = scale_to_cover(original_image, banner_size)
                    self.songs[i]["original_img"] = original_image
                    dominant_color = get_dominant_color(original_image, DEFAULT_ACCENT_COLOR)
                    self.songs[i]["accent_color"] = self._vibrant_color(dominant_color)
                except pygame.error:
                    self.songs[i].update(
                        {"banner_img": None, "original_img": None, "accent_color": DEFAULT_ACCENT_COLOR})
            else:
                self.songs[i].update({"banner_img": None, "original_img": None, "accent_color": DEFAULT_ACCENT_COLOR})

            if song["blurred_image_path"] and os.path.exists(song["blurred_image_path"]):
                try:
                    blurred_img = pygame.image.load(song["blurred_image_path"]).convert()
                    self.songs[i]["blurred_background_hq"] = pygame.transform.smoothscale(blurred_img,
                                                                                          self.screen_rect.size)
                except pygame.error:
                    self.songs[i]["blurred_background_hq"] = None
            else:
                self.songs[i]["blurred_background_hq"] = None

    def select_song(self, index):
        self.selected_index = index
        self.selected_song = self.songs[self.selected_index]
        self.accent_color = self.selected_song["accent_color"]

        if self.selected_song.get("blurred_background_hq"):
            self.background_img = self.selected_song["blurred_background_hq"]
        elif self.selected_song.get("original_img"):
            self.background_img = self._create_fallback_blur(self.selected_song["original_img"])
        else:
            self.background_img = pygame.Surface(self.screen_rect.size);
            self.background_img.fill((20, 20, 20))


        self.play_song_preview()

    def play_song_preview(self):
        """ Loads and plays the music for the currently selected song. """
        song = self.songs[self.selected_index]
        audio_path = song.get("audio_path")
        preview_time_s = song.get("preview_time_ms", 10000) / 1000.0

        if audio_path and os.path.exists(audio_path):
            try:
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play(start=preview_time_s)
                print(f"Playing preview for {song['title']} at {preview_time_s}s")
            except pygame.error as e:
                print(f"Error playing music file {audio_path}: {e}")
        else:
            pygame.mixer.music.stop()

    def get_event(self, event):
        super().get_event(event)

        if not self.songs or self.transition_state != "static": return

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                new_index = (self.selected_index + 1) % len(self.songs)
                self.select_song(new_index)
            elif event.key == pygame.K_UP:
                new_index = (self.selected_index - 1 + len(self.songs)) % len(self.songs)
                self.select_song(new_index)
            elif event.key == pygame.K_RETURN:

                pygame.mixer.music.fadeout(500)

                self.persist["selected_song_data"] = self.selected_song
                self.persist["selected_song_data"]["final_background"] = self.background_img

                self.go_to_next_state()

    def draw(self, surface):
        surface.blit(self.background_img, (0, 0))
        if not self.songs:
            draw_text(surface, "No Songs Found in assets/songs", self.screen_rect.center, self.font_title, WHITE,
                      text_rect_origin='center')
            return

        progress = 1 - (self.transition_timer / self.transition_time)
        eased_progress = self.ease_out_cubic(progress)

        info_panel_start_x, info_panel_end_x = -500, 40
        song_list_start_x, song_list_end_x = self.screen_rect.width + 50, self.screen_rect.width - 550

        if self.transition_state == "in":
            info_panel_x = info_panel_start_x + (info_panel_end_x - info_panel_start_x) * eased_progress
            song_list_x = song_list_start_x + (song_list_end_x - song_list_start_x) * eased_progress
        elif self.transition_state == "out":
            info_panel_x = info_panel_end_x + (info_panel_start_x - info_panel_end_x) * eased_progress
            song_list_x = song_list_end_x + (song_list_start_x - song_list_end_x) * eased_progress
        else:  # static
            info_panel_x = info_panel_end_x
            song_list_x = song_list_end_x

        ui_surface = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
        self.draw_info_panel(ui_surface, int(info_panel_x))
        self.draw_song_list(ui_surface, int(song_list_x))
        self.draw_header(ui_surface, int(song_list_x))

        ui_surface.set_alpha(self.get_transition_alpha())
        surface.blit(ui_surface, (0, 0))

    def draw_info_panel(self, surface, panel_x):
        panel_y, panel_width, border_radius = 50, 450, 12
        title_rect = pygame.Rect(panel_x, panel_y, panel_width, 80)
        pygame.draw.rect(surface, (15, 15, 15, 200), title_rect, border_radius=border_radius)
        pygame.draw.line(surface, self.accent_color, title_rect.topleft + pygame.Vector2(border_radius, 0),
                         title_rect.topright - pygame.Vector2(border_radius, 0), 4)
        draw_text(surface, self.selected_song["title"], (title_rect.left + 25, title_rect.centery - 12),
                  self.font_title, WHITE, text_rect_origin='topleft')
        draw_text(surface, self.selected_song["artist"], (title_rect.left + 25, title_rect.centery + 18),
                  self.font_artist, (180, 180, 180), text_rect_origin='topleft')

        stats_rect = pygame.Rect(panel_x, panel_y + 100, panel_width, 60)
        pygame.draw.rect(surface, (15, 15, 15, 200), stats_rect, border_radius=border_radius)
        stats = [("NOTES", self.selected_song["notes"]), ("LENGTH", self.selected_song["length"]),
                 ("BPM", self.selected_song["bpm"])]
        for i, (label, value) in enumerate(stats):
            x_pos = stats_rect.left + (panel_width / len(stats)) * (i + 0.5)
            draw_text(surface, label, (x_pos, stats_rect.top + 15), self.font_stats_label, (150, 150, 150),
                      text_rect_origin='center')
            draw_text(surface, str(value), (x_pos, stats_rect.top + 38), self.font_stats_value, WHITE,
                      text_rect_origin='center')

    def draw_song_list(self, surface, list_x):
        center_y, banner_h, banner_w, border_radius = self.screen_rect.centery, 100, 500, 10
        display_range = range(self.selected_index - 3, self.selected_index + 4)
        for i_offset, list_index_raw in enumerate(display_range):
            if 0 <= list_index_raw < len(self.songs):
                song = self.songs[list_index_raw]
                y_pos = center_y + (i_offset - 3) * (banner_h - 10)
                banner_rect = pygame.Rect(list_x, y_pos, banner_w, banner_h - 20)
                if song.get("banner_img"):
                    clip_surface = pygame.Surface(banner_rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(clip_surface, WHITE, (0, 0, *banner_rect.size), border_radius=border_radius)
                    clip_surface.blit(song["banner_img"], (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                    surface.blit(clip_surface, banner_rect.topleft)
                else:
                    pygame.draw.rect(surface, (30, 30, 30), banner_rect, border_radius=border_radius)
                overlay = pygame.Surface(banner_rect.size, pygame.SRCALPHA)
                gradient = pygame.Surface((2, 2), pygame.SRCALPHA);
                pygame.draw.line(gradient, (0, 0, 0, 200), (0, 0), (1, 0));
                pygame.draw.line(gradient, (0, 0, 0, 50), (0, 1), (1, 1))
                gradient = pygame.transform.smoothscale(gradient, (banner_rect.width, banner_rect.height))
                overlay.blit(gradient, (0, 0));
                surface.blit(overlay, banner_rect.topleft)
                draw_text(surface, song["title"], (banner_rect.left + 25, banner_rect.centery - 10),
                          self.font_banner_title, WHITE, text_rect_origin='topleft')
                draw_text(surface, song["artist"], (banner_rect.left + 25, banner_rect.centery + 15),
                          self.font_banner_artist, (200, 200, 200), text_rect_origin='topleft')
                if list_index_raw == self.selected_index:
                    pygame.draw.rect(surface, song["accent_color"], banner_rect, 3, border_radius=border_radius)

    def draw_header(self, surface, header_x):
        btn_width, btn_height, btn_y, border_radius = 100, 35, 40, 8
        buttons = ["SORT", "GROUP", "COLLECTION"]
        btn_x_start = header_x + 500 - (btn_width * len(buttons) + (len(buttons) - 1) * 10)
        for i, text in enumerate(buttons):
            btn_x = btn_x_start + i * (btn_width + 10)
            btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
            pygame.draw.rect(surface, (15, 15, 15, 200), btn_rect, border_radius=border_radius)
            draw_text(surface, text, btn_rect.center, self.font_header, (200, 200, 200), text_rect_origin='center')

