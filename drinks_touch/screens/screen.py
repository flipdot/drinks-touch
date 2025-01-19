import pygame

import config
from config import Color
from elements.base_elm import BaseElm
from screen import get_screen_surface
from screens.screen_manager import ScreenManager


class Screen:

    idle_timeout = 10
    nav_bar_visible = True

    def __init__(self, width=None, height=None):
        if width is None or height is None:
            screen_surface = get_screen_surface()
            width = width or screen_surface.get_width()
            height = height or screen_surface.get_height()
        self.width = width
        self.height = height
        self.objects: list[BaseElm] = []
        self._alert = None
        self.on_create()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def render(self, dt):
        surface = pygame.Surface((self.width, self.height))
        surface.fill(Color.BACKGROUND.value)
        if config.DEBUG_UI_ELEMENTS:
            debug_surface = pygame.Surface((self.width, self.height))
        else:
            debug_surface = None
        for o in self.objects:
            if not o.visible:
                continue
            obj_surface = o.render(dt)
            if obj_surface is not None:
                surface.blit(obj_surface, o.screen_pos)
            if config.DEBUG_UI_ELEMENTS:
                obj_debug_surface = o.render_debug()
                if obj_debug_surface is not None:
                    debug_surface.blit(obj_debug_surface, o.screen_pos)
        for o in self.objects:
            if o.visible:
                obj_overlay_surface = o.render_overlay()
                if obj_overlay_surface is not None:
                    surface.blit(obj_overlay_surface, o.screen_pos)
        if self._alert:
            alert = self.render_alert()
            surface.blit(alert, (0, 0))

        return surface, debug_surface

    def render_alert(self) -> pygame.Surface:
        alert_text_surface = pygame.font.Font(None, 30).render(
            self._alert, True, (255, 0, 0)
        )
        padding = 10
        alert_box = pygame.Surface(
            (
                alert_text_surface.get_width() + padding * 2,
                alert_text_surface.get_height() + padding * 2,
            ),
            pygame.SRCALPHA,
        )

        alert_box.fill((255, 255, 255))
        alert_box.blit(alert_text_surface, (padding, padding))

        alert = pygame.Surface((self.width, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        alert.fill((0, 0, 0, 180))

        alert.blit(
            alert_box,
            (
                (self.width - alert_box.get_width()) // 2,
                (config.SCREEN_HEIGHT - alert_box.get_height()) // 2,
            ),
        )
        return alert

    def event(self, event) -> BaseElm | None:
        if self._alert:
            if event.type == pygame.MOUSEBUTTONUP:
                self._alert = None
            return
        for obj in self.objects[::-1]:
            if consumed_by := obj.event(event):
                return consumed_by

    @staticmethod
    def back():
        ScreenManager.instance.go_back()

    @staticmethod
    def goto(screen: "Screen", *args, **kwargs):
        ScreenManager.instance.set_active(screen, *args, **kwargs)

    @staticmethod
    def home():
        ScreenManager.instance.set_default()

    def alert(self, text: str):
        self._alert = text

    # lifecycle inspired by https://developer.android.com/guide/components/activities/activity-lifecycle
    # Not all yet implemented

    def on_create(self, *args, **kwargs):
        pass

    def on_start(self, *args, **kwargs):
        pass

    # def on_resume(self):
    #     pass

    # def on_pause(self):
    #     pass

    def on_stop(self, *args, **kwargs):
        pass

    def on_destroy(self, *args, **kwargs):
        pass
