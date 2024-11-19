import pygame

from screen import get_screen_surface

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens.screen import Screen


class ScreenManager:
    instance = None

    def __init__(self):
        self.current_screen = None
        self.surface = get_screen_surface()
        self.screen_history = []
        self.reset_history()

    def set_default(self):
        from screens.wait_scan import WaitScanScreen

        self.reset_history()
        self.set_active(WaitScanScreen())

    def set_active(self, screen, *args, **kwargs):
        self.screen_history.append(screen)
        self.current_screen = screen
        screen.on_start(*args, **kwargs)

    def get_active(self) -> "Screen":
        return self.current_screen

    def go_back(self):
        self.screen_history.pop()  # remove yourself
        last = self.screen_history.pop()
        return self.set_active(last)

    def reset_history(self):
        self.screen_history = []  # reset history

    def render(self, dt):
        current_screen = self.get_active()
        surface, debug_surface = current_screen.render(dt)
        if surface is not None:
            self.surface.blit(surface, (0, 0))
        if debug_surface is not None:
            self.surface.blit(debug_surface, (0, 0), special_flags=pygame.BLEND_ADD)

    @staticmethod
    def get_instance():
        return ScreenManager.instance

    @staticmethod
    def set_instance(instance):
        ScreenManager.instance = instance
