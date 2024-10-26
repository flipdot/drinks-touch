import pygame

import config
import math


class BaseOverlay:
    def __init__(self, screen):
        self.screen = screen

    def render(self, dt):
        pass

    def events(self, events):
        pass


class MouseOverlay(BaseOverlay):
    def __init__(self, screen):
        super().__init__(screen)
        self.mouse_pos = (0, 0)
        self.click_pos = (0, 0)
        self.color = config.COLORS["infragelb"]
        self.tick = 0

    def render(self, dt):
        self.tick += dt
        radius_inner = 50 * math.sin(self.tick * 1.3)
        radius_outer = 50 * math.sin(self.tick * 2)
        # Avoid infinite loop
        if self.tick > 2:
            return
        if radius_inner >= radius_outer:
            return
        # pygame.draw.circle(self.screen, self.color, self.click_pos, radius)
        for angel in range(0, 360, 30):
            start_pos = (
                self.click_pos[0] + radius_inner * math.cos(math.radians(angel)),
                self.click_pos[1] + radius_inner * math.sin(math.radians(angel)),
            )
            end_pos = (
                self.click_pos[0] + radius_outer * math.cos(math.radians(angel)),
                self.click_pos[1] + radius_outer * math.sin(math.radians(angel)),
            )
            # pygame.draw.circle(self.screen, (255, 0, 255), start_pos, 1)
            # pygame.draw.circle(self.screen, (0, 255, 0), end_pos, 1)
            pygame.draw.line(
                self.screen,
                self.color,
                start_pos,
                end_pos,
                width=3,
            )

    def events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.click_pos = event.pos
                self.reset()

    def reset(self):
        self.tick = 0
