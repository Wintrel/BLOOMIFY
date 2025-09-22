import pygame
from .base import BaseState
from settings import *
from .utility import draw_text


class MainMenu(BaseState):
    def __init__(self):
        super(MainMenu, self).__init__()
        self.next_state = "SONG_SELECT"
        self.transition_duration = 0.5  # Fade out over 0.5 seconds

        # Timers
        self.time_active = 0
        self.animation_stage = 0
        self.stage_timers = {
            0: 0.3,  # Delay
            1: 1.5,  # Outline draw duration
            2: 1.0,  # Subtitle fade
            3: -1
        }

        # Fonts
        self.title_font = pygame.font.Font(None, 120)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.click_font = pygame.font.Font(None, 24)

        # Animation vars
        self.reveal_progress = 0
        self.subtitle_alpha = 0
        self.click_alpha = 0
        self.click_pulse_dir = 1

        # Pre-render hollow text
        temp_title = self.title_font.render("BLOOMIFY", True, WHITE)
        self.title_rect = temp_title.get_rect(center=self.screen_rect.center)

        self.title_outline_surf = pygame.Surface(self.title_rect.size, pygame.SRCALPHA)
        # This call now works with the new utility.py
        draw_text(self.title_outline_surf, "BLOOMIFY", self.title_outline_surf.get_rect().center,
                  self.title_font, (0, 0, 0, 0), outline_width=2, outline_color=WHITE, outline_only=True,
                  text_rect_origin='center')

        self.max_radius = (self.title_rect.width ** 2 + self.title_rect.height ** 2) ** 0.5 / 2

    def get_event(self, event):
        super().get_event(event)
        # On any click or key press, start the transition out
        if self.animation_stage >= 3 and self.transition_state == "normal":
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                self.trigger_transition_out()

    def update(self, dt):
        super().update(dt)  # This handles the transition timer

        self.time_active += dt / 1000.0  # Convert dt to seconds

        if self.animation_stage < 3:
            # --- Intro Animation Logic ---
            if self.time_active > self.stage_timers.get(self.animation_stage, 0):
                self.time_active = 0
                self.animation_stage += 1

            if self.animation_stage == 1:  # Outline reveal
                self.reveal_progress = min(1, self.time_active / self.stage_timers[1])
            elif self.animation_stage == 2:  # Subtitle fade
                self.subtitle_alpha = min(255, int(255 * (self.time_active / self.stage_timers[2])))
        else:
            # --- Pulsing Text Logic ---
            pulse_speed = 350
            self.click_alpha += pulse_speed * (dt / 1000.0) * self.click_pulse_dir
            if self.click_alpha >= 255:
                self.click_alpha = 255
                self.click_pulse_dir = -1
            elif self.click_alpha <= 50:
                self.click_alpha = 50
                self.click_pulse_dir = 1

    def draw(self, surface):
        surface.fill(BLACK)

        # Create a temporary surface to draw all UI elements on.
        # This allows us to fade the entire screen at once.
        ui_surface = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)

        # Stage 1+: reveal outline via circular mask
        if self.animation_stage >= 1:
            radius = int(self.max_radius * self.reveal_progress)
            mask = pygame.Surface(self.title_rect.size, pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), mask.get_rect().center, radius)
            reveal_surf = pygame.Surface(self.title_rect.size, pygame.SRCALPHA)
            reveal_surf.blit(self.title_outline_surf, (0, 0))
            reveal_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            ui_surface.blit(reveal_surf, self.title_rect)

        # Stage 2+: Subtitle fade
        if self.animation_stage >= 2:
            subtitle_pos = (self.screen_rect.centerx, self.screen_rect.centery + 80)
            draw_text(ui_surface, "AN RHYTHM GAME", subtitle_pos, self.subtitle_font,
                      color=(*WHITE, int(self.subtitle_alpha)), text_rect_origin='center')

        # Stage 3+: "Click anywhere" pulse
        if self.animation_stage >= 3:
            click_pos = (self.screen_rect.centerx, self.screen_rect.height - 50)
            draw_text(ui_surface, "Click anywhere to bloom", click_pos, self.click_font,
                      color=(*WHITE, int(self.click_alpha)), text_rect_origin='center')

        # --- Apply Transition Fade ---
        ui_surface.set_alpha(self.transition_alpha)
        surface.blit(ui_surface, (0, 0))

