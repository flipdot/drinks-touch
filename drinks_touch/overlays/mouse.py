import pygame
from pygame.event import EventType

import config
import math

from screens.screen_manager import ScreenManager
from .base import BaseOverlay


class MouseOverlay(BaseOverlay):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__(screen_manager)
        self.mouse_pos = (0, 0)
        self.click_pos = (0, 0)
        self.mouse_path = []
        self.color = config.Color.PRIMARY
        self.mouse_pressed = False

    def render(self):
        self._render_click_animation()
        self._render_mouse_path()
        self._render_mouse_pos()

    def _render_click_animation(self):
        radius_inner = 50 * math.sin(self.t * 1.3)
        radius_outer = 50 * math.sin(self.t * 2)
        # Avoid infinite loop
        if self.t > 2:
            return
        if radius_inner >= radius_outer:
            return
        for angel in range(0, 360, 30):
            start_pos = (
                self.click_pos[0] + radius_inner * math.cos(math.radians(angel)),
                self.click_pos[1] + radius_inner * math.sin(math.radians(angel)),
            )
            end_pos = (
                self.click_pos[0] + radius_outer * math.cos(math.radians(angel)),
                self.click_pos[1] + radius_outer * math.sin(math.radians(angel)),
            )
            pygame.draw.line(
                self.screen,
                self.color.value,
                start_pos,
                end_pos,
                width=3,
            )
            if ScreenManager.instance.DEBUG_LEVEL >= 2:
                pygame.draw.circle(self.screen, (255, 0, 255), start_pos, 3)
                pygame.draw.circle(self.screen, (0, 255, 255), end_pos, 3)

    def _render_mouse_pos(self):
        if not self.mouse_pressed:
            return
        pygame.draw.circle(self.screen, self.color.value, self.mouse_pos, 5)

    def _render_mouse_path(self):
        if len(self.mouse_path) > 2:
            last_pos = self.mouse_path[0][1]
            new_mouse_path = []
            surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            for i, (color, pos) in enumerate(self.mouse_path):
                pygame.draw.line(surface, color, last_pos, pos, 1)
                color = (color[0], color[1], color[2], max(0, color[3] - 30))
                if color[3] > 0:
                    new_mouse_path.append((color, pos))
                last_pos = pos
            self.mouse_path = new_mouse_path
            self.screen.blit(surface, (0, 0))

    def events(self, events: list[EventType]):
        self.mouse_pressed = pygame.mouse.get_pressed()[0]
        if not self.mouse_pressed:
            self.mouse_path = []
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                if self.mouse_pressed:
                    self.mouse_path.append((self.color.value, event.pos))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.click_pos = event.pos
                self.reset()

    def reset(self):
        self.t = 0
