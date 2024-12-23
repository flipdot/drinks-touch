import pygame

from config import Color, Font
from elements import Button, Progress
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
        self.timeout_widget = Progress(
            pos=(425, 10),
            speed=1 / 5.0,
            on_elapsed=lambda: self.set_default(),
        )
        self.objects = [
            Button(
                text=" ‹ ",
                pos=(5, 5),
                on_click=self.go_back,
                font=Font.MONOSPACE,
                size=30,
            ),
            self.timeout_widget,
        ]

    def set_idle_timeout(self, timeout: int):
        """
        Go to the home screen after `timeout` seconds of inactivity.
        Pass 0 if no automatic timeout should occur.
        """
        if timeout == 0:
            self.timeout_widget.stop()
            return
        self.timeout_widget.speed = 1 / timeout
        self.timeout_widget.start()

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
        self.set_idle_timeout(screen.idle_timeout)

    def get_active(self) -> "Screen | None":
        if len(self.screen_history) == 0:
            return None
        return self.screen_history[-1]

    def go_back(self):
        prev_screen = self.get_active()
        prev_screen.on_stop()
        prev_screen.on_destroy()
        self.screen_history.pop()

        new_active_screen = self.get_active()
        new_active_screen.on_start()
        self.set_idle_timeout(new_active_screen.idle_timeout)

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
        if pygame.mouse.get_pressed()[0]:
            self.set_idle_timeout(0)
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.set_idle_timeout(screen.idle_timeout)
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
    def get_instance() -> "ScreenManager":
        return ScreenManager.instance

    @staticmethod
    def set_instance(instance):
        ScreenManager.instance = instance
