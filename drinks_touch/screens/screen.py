import pygame

import config
from config import Color
from elements.base_elm import BaseElm
from screen import get_screen_surface
from screens.screen_manager import ScreenManager


class Screen:

    idle_timeout = 10
    nav_bar_visible = True
    background_color = Color.BACKGROUND.value

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
        self._keyboard_input = ""
        self.dirty = True
        self.last_hash = 0
        self.surface: pygame.Surface | None = None
        self.debug_surface: pygame.Surface | None = None

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def calculate_hash(self):
        return hash(
            (
                self.width,
                self.height,
                self._alert,
                tuple(o.calculate_hash() for o in self.objects),
            )
        )

    def tick(self, dt: float):
        for o in self.objects:
            o.tick(dt)

    def _render(self) -> tuple[pygame.Surface, pygame.Surface | None]:
        surface = pygame.Surface((self.width, self.height))
        surface.fill(self.background_color)
        if ScreenManager.instance.DEBUG_LEVEL >= 3:
            debug_surface = pygame.Surface((self.width, self.height))
        else:
            debug_surface = None
        for o in self.objects:
            if not o.visible:
                continue
            if obj_surface := o.render():
                surface.blit(obj_surface, o.screen_pos)
                if ScreenManager.instance.DEBUG_LEVEL >= 3:
                    if obj_debug_surface := o.render_debug():
                        debug_surface.blit(obj_debug_surface, o.screen_pos)
        for o in self.objects:
            if o.visible and (overlay_surface := o.render_overlay()):
                surface.blit(overlay_surface, o.screen_pos)
        if self._alert:
            alert = self.render_alert()
            surface.blit(alert, (0, 0))

        return surface, debug_surface

    def render(self) -> tuple[pygame.Surface, pygame.Surface | None]:
        """
        Caches the result of the internal `_render` method
        """
        if self.last_hash != (new_hash := self.calculate_hash()):
            self.dirty = True
            self.last_hash = new_hash
        if self.dirty:
            self.surface, self.debug_surface = self._render()
            self.dirty = False
        return self.surface, self.debug_surface

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

    def event(self, event) -> bool:
        if self._alert:
            if event.type == pygame.MOUSEBUTTONUP:
                self._alert = None
            return False
        for obj in self.objects[::-1]:
            if obj.event(event):
                return True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                self.on_barcode(self._keyboard_input)
                self._keyboard_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self._keyboard_input = self._keyboard_input[:-1]
            else:
                self._keyboard_input += event.unicode
        return False

    def on_barcode(self, barcode: str):
        pass

    @staticmethod
    def back():
        ScreenManager.instance.go_back()

    @staticmethod
    def goto(screen: "Screen", replace=False, *args, **kwargs):
        ScreenManager.instance.set_active(screen, replace=replace, *args, **kwargs)

    @staticmethod
    def home():
        ScreenManager.instance.set_default()

    def alert(self, text: str):
        self._alert = text

    @property
    def show_alert(self):
        return self._alert is not None

    @show_alert.setter
    def show_alert(self, value):
        if not value:
            self._alert = None

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
