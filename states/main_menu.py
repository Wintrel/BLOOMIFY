import pygame
from settings import *
from .base import BaseState
from .utility import draw_text


class MainMenu(BaseState):
    def __init__(self):
        super(MainMenu, self).__init__()
        self.next_state = "SONG_SELECT"

        # --- Timers ---
        self.time_active = 0
        self.animation_stage = 0
        self.stage_timers = {
            0: 0.3,  # Initial delay
            1: 1.2,  # Outline reveal duration
            2: 0.8,  # Subtitle fade-in
            3: -1  # Final static stage
        }

        # --- Fonts ---
        self.title_font = pygame.font.Font(None, 120)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.click_font = pygame.font.Font(None, 24)

        # --- Animation Variables ---
        self.reveal_progress = 0
        self.subtitle_alpha = 0
        self.click_alpha = 0
        self.click_pulse_dir = 1

        # --- Pre-calculate title rect ---
        self.title_pos = self.screen_rect.center

    def update(self, dt):
        super().update(dt)
        self.time_active += dt / 1000.0

        # --- Animation Stage Controller ---
        if self.animation_stage < 3 and self.time_active > self.stage_timers[self.animation_stage]:
            self.time_active = 0  # Reset timer for the next stage
            self.animation_stage += 1
            # Finalize progress of previous stages
            if self.animation_stage == 2: self.reveal_progress = 1
            if self.animation_stage == 3: self.subtitle_alpha = 255

        # --- Update Animation Values ---
        if self.animation_stage == 1:  # Outline reveal
            self.reveal_progress = self.time_active / self.stage_timers[1]

        elif self.animation_stage == 2:  # Subtitle fade
            self.subtitle_alpha = 255 * (self.time_active / self.stage_timers[2])

        elif self.animation_stage == 3:  # Click prompt pulse
            pulse_speed = 150  # Alpha units per second
            self.click_alpha += pulse_speed * (dt / 1000.0) * self.click_pulse_dir
            if self.click_alpha >= 255:
                self.click_alpha = 255
                self.click_pulse_dir = -1
            elif self.click_alpha <= 50:
                self.click_alpha = 50
                self.click_pulse_dir = 1

    def get_event(self, event):
        super().get_event(event)
        if self.transition_state != "static": return
        if self.animation_stage == 3:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.go_to_next_state()
            if event.type == pygame.MOUSEBUTTONUP:
                self.go_to_next_state()

    def draw(self, surface):
        surface.fill(BLACK)

        # --- Draw Title ---
        if self.animation_stage >= 1:
            # 1. Draw the outline first
            draw_text(surface, "BLOOMIFY", self.title_pos, self.title_font, WHITE,
                      outline_width=2, outline_color=WHITE, alpha=self.get_transition_alpha())


            # Create a clipping rect that grows with the reveal animation
            title_render_rect = self.title_font.render("BLOOMIFY", True, WHITE).get_rect(center=self.title_pos)
            clip_width = int(title_render_rect.width * self.reveal_progress)
            clip_rect = pygame.Rect(title_render_rect.left, title_render_rect.top, clip_width, title_render_rect.height)

            # Draw the filled text, but only within the clipping area
            surface.set_clip(clip_rect)
            draw_text(surface, "BLOOMIFY", self.title_pos, self.title_font, WHITE, alpha=self.get_transition_alpha())
            surface.set_clip(None)  # Reset clipping area

        # --- Draw Subtitle ---
        if self.animation_stage >= 2:
            subtitle_pos = (self.screen_rect.centerx, self.screen_rect.centery + 80)
            draw_text(surface, "AN RHYTHM GAME", subtitle_pos, self.subtitle_font,
                      color=WHITE, alpha=min(self.subtitle_alpha, self.get_transition_alpha()))

        # --- Draw Click Prompt ---
        if self.animation_stage == 3:
            click_pos = (self.screen_rect.centerx, self.screen_rect.height - 50)
            draw_text(surface, "Click anywhere or press Enter to bloom", click_pos, self.click_font,
                      color=WHITE, alpha=min(self.click_alpha, self.get_transition_alpha()))

