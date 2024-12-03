import pygame

from config import Color, Font
from elements import Button
from screen import get_screen_surface

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens.screen import Screen


class ScreenManager:
    instance = None
    MENU_BAR_HEIGHT = 65

    def __init__(self):
        self.current_screen = None
        self.surface = get_screen_surface()
        self.screen_history: list[Screen] = []
        self.objects = [
            Button(
                text=" ‹ ",
                pos=(5, 5),
                on_click=self.go_back,
                font=Font.MONOSPACE,
                size=30,
            )
        ]

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

    @property
    def nav_bar_visible(self):
        return len(self.screen_history) > 1

    def render(self, dt):
        self.surface.fill(Color.BACKGROUND.value)
        current_screen = self.get_active()
        surface, debug_surface = current_screen.render(dt)
        if surface is not None:
            self.surface.blit(surface, (0, 0))
        if debug_surface is not None:
            self.surface.blit(debug_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        if self.nav_bar_visible:
            menu_bar = pygame.Surface((self.surface.get_width(), self.MENU_BAR_HEIGHT))
            menu_bar.fill(Color.NAVBAR_BACKGROUND.value)
            # draw top border
            pygame.draw.line(
                menu_bar, Color.PRIMARY.value, (0, 0), (menu_bar.get_width(), 0)
            )
            for obj in self.objects:
                obj_surface = obj.render(dt)
                menu_bar.blit(obj_surface, obj.screen_pos)
            # back_surface = pygame.Surface((100, 50))
            # back_surface.fill((255, 0, 255))
            # back_surface.blit(
            #     pygame.font.Font(None, 30).render("Back", True, (0, 0, 0)), (10, 10)
            # )
            self.surface.blit(
                menu_bar, (0, self.surface.get_height() - menu_bar.get_height())
            )

    def events(self, events):
        screen = self.get_active()
        for event in events:
            if self.nav_bar_visible and hasattr(event, "pos"):
                transformed_pos = (
                    event.pos[0],
                    event.pos[1] - self.surface.get_height() + self.MENU_BAR_HEIGHT,
                )
                for obj in self.objects:
                    if getattr(event, "consumed", False):
                        continue
                    obj.event(event, transformed_pos)
            if getattr(event, "consumed", False):
                continue
            screen.event(event)
            # screen.events(events)

    @staticmethod
    def get_instance():
        return ScreenManager.instance

    @staticmethod
    def set_instance(instance):
        ScreenManager.instance = instance
