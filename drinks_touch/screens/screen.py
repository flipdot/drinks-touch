import pygame

import config
from screens.screen_manager import ScreenManager


class Screen(object):
    def __init__(self, screen):
        self.screen = screen
        self.objects = []

    def render(self, dt):
        for o in self.objects:
            if o.visible():
                surface = o.render(dt)
                if surface is not None:
                    self.screen.blit(surface, o.screen_pos)
        if config.DEBUG_UI_ELEMENTS:
            self.render_debug()

    def render_debug(self):
        for o in self.objects:
            if o.visible():
                w = o.width
                h = o.height
                x = o.screen_pos[0]
                y = o.screen_pos[1]
                pygame.draw.rect(self.screen, (255, 0, 255), (x, y, w, h), width=1)
                pygame.draw.line(
                    self.screen, (255, 0, 255), (x, y), (x + w, y + h), width=1
                )
                pygame.draw.line(
                    self.screen, (255, 0, 255), (x + w, y), (x, y + h), width=1
                )

    def events(self, events):
        for o in self.objects:
            o.events(events)

    @staticmethod
    def back():
        ScreenManager.get_instance().go_back()
