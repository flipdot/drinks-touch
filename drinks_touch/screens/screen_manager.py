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

    def set_default(self):
        from screens.wait_scan import WaitScanScreen

        self.reset_history()
        self.set_active(WaitScanScreen())

    def set_active(self, screen: "Screen", *args, **kwargs):
        current_screen = self.get_active()
        if current_screen is not None:
            current_screen.on_stop()
        self.screen_history.append(screen)
        screen.on_start(*args, **kwargs)

    def get_active(self) -> "Screen | None":
        if len(self.screen_history) == 0:
            return None
        return self.screen_history[-1]

    def go_back(self):
        self.get_active().on_stop()
        self.get_active().on_destroy()
        self.screen_history.pop()
        self.get_active().on_start()

    def reset_history(self):
        self.screen_history = []

    def render(self, dt):
        current_screen = self.get_active()
        surface, debug_surface = current_screen.render(dt)
        if surface is not None:
            self.surface.blit(surface, (0, 0))
        if debug_surface is not None:
            self.surface.blit(debug_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        if len(self.screen_history) > 1:
            back_surface = pygame.Surface((100, 50))
            back_surface.fill((255, 0, 255))
            back_surface.blit(
                pygame.font.Font(None, 30).render("Back", True, (0, 0, 0)), (10, 10)
            )
            self.surface.blit(back_surface, (0, self.surface.get_height() - 50))

    @staticmethod
    def get_instance():
        return ScreenManager.instance

    @staticmethod
    def set_instance(instance):
        ScreenManager.instance = instance
