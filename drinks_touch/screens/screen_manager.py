import pygame
from pygame.event import EventType

import config
from config import Color, Font
from elements import Button, Progress, Label
from elements.base_elm import BaseElm
from overlays.keyboard import KeyboardOverlay
from screen import get_screen_surface

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens.screen import Screen


class ScreenManager:
    instance: "ScreenManager" = None
    MENU_BAR_HEIGHT = 65
    DEBUG_LEVEL = int(config.DEBUG_LEVEL)
    MAX_DEBUG_LEVEL = 3

    def __init__(self):
        assert ScreenManager.instance is None, "ScreenManager is a singleton"
        self.ts = 0
        self.current_screen = None
        self.surface = get_screen_surface()
        self.screen_history: list[Screen] = []
        self.timeout_widget = Progress(
            pos=(config.SCREEN_WIDTH - 5, 10),
            align_right=True,
            speed=1 / 5.0,
            on_elapsed=lambda: self.set_default(),
        )
        self.default_objects = [
            Button(
                text=" ‹ ",
                pos=(5, 5),
                on_click=self.go_back,
                font=Font.MONOSPACE,
                size=30,
            ),
            self.timeout_widget,
        ]
        self.active_keyboard_objects: list[BaseElm] = [
            Label(
                text=" v ",
                pos=(23, 20),
                # on_click=self.hide_keyboard,
                font=Font.MONOSPACE,
                size=20,
            ),
            self.timeout_widget,
        ]
        self.active_object = None
        ScreenManager.instance = self

    @property
    def active_object(self) -> BaseElm | None:
        return self._active_object

    @active_object.setter
    def active_object(self, value: BaseElm | None):
        self._active_object = value
        if value is not None:
            if settings := value.keyboard_settings:
                KeyboardOverlay.instance.apply_settings(settings)

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

    def set_active(
        self, screen: "Screen", replace=False, replace_last_n=1, *args, **kwargs
    ):
        current_screen = self.get_active()
        if current_screen is not None:
            current_screen.on_stop()
        if replace:
            self.screen_history = self.screen_history[:-replace_last_n]
        self.screen_history.append(screen)
        self.active_object = None
        screen.on_start(*args, **kwargs)
        self.set_idle_timeout(screen.idle_timeout)

    def get_active(self) -> "Screen | None":
        if len(self.screen_history) == 0:
            return None
        return self.screen_history[-1]

    def hide_keyboard(self):
        self.active_object = None

    def go_back(self):
        prev_screen = self.get_active()
        if prev_screen.show_alert:
            prev_screen.show_alert = False
            return
        prev_screen.on_stop()
        prev_screen.on_destroy()
        self.screen_history.pop()

        self.active_object = None

        new_active_screen = self.get_active()
        new_active_screen.on_start()
        self.set_idle_timeout(new_active_screen.idle_timeout)

    def reset_history(self):
        self.screen_history = []

    @property
    def nav_bar_visible(self):
        if len(self.screen_history) <= 1:
            return False
        return self.get_active().nav_bar_visible

    def tick(self, dt: float):
        self.ts += dt
        if self.active_object:
            self.active_object.ts_active += dt
        obj_list = (
            self.active_keyboard_objects
            if self.keyboard_visible
            else self.default_objects
        )
        if self.nav_bar_visible:
            for obj in obj_list:
                obj.tick(dt)
        self.get_active().tick(dt)

    def render(self, fps):
        self.surface.fill(Color.BACKGROUND.value)
        current_screen = self.get_active()
        surface, debug_surface = current_screen.render()
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
            obj_list = (
                self.active_keyboard_objects
                if self.keyboard_visible
                else self.default_objects
            )
            for obj in obj_list:
                if not obj.visible:
                    continue
                menu_bar.blit(obj.render(), obj.screen_pos)
            # back_surface = pygame.Surface((100, 50))
            # back_surface.fill((255, 0, 255))
            # back_surface.blit(
            #     pygame.font.Font(None, 30).render("Back", True, (0, 0, 0)), (10, 10)
            # )
            self.surface.blit(
                menu_bar, (0, self.surface.get_height() - menu_bar.get_height())
            )

        if self.DEBUG_LEVEL >= 1:
            info = pygame.display.Info()
            font = pygame.font.Font(None, 30)
            resolution_text = font.render(
                f"{info.current_w}x{info.current_h}", True, (255, 255, 255)
            )
            fps_text = font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
            self.surface.blit(resolution_text, (10, 10))
            self.surface.blit(
                fps_text, (self.surface.get_width() - fps_text.get_width() - 10, 10)
            )

    def events(self, events: list[EventType]):
        screen = self.get_active()
        if pygame.mouse.get_pressed()[0]:
            self.set_idle_timeout(0)
        for event in events:
            if (
                event.type == pygame.MOUSEBUTTONUP
                and event.button == 1
                or event.type == pygame.KEYDOWN
            ):
                self.set_idle_timeout(screen.idle_timeout)
                screen.show_alert = False
            if event.dict.get("consumed"):
                # Don't process events that have already been consumed.
                # But still reset the idle timeout, so that the screen doesn't
                # disappear while the user is interacting with it.
                # This is why the idle timeout is set before this check.
                continue
            if event.type == pygame.MOUSEBUTTONUP:
                ScreenManager.instance.active_object = None
            if self.nav_bar_visible and hasattr(event, "pos"):
                # Handle clicks on the navbar itself.
                # This is why we need to calculate the transformed_pos,
                # because the event.pos is relative to the whole screen,
                # and the navbar is placed at the bottom of the screen.
                transformed_pos = (
                    event.pos[0],
                    event.pos[1] - self.surface.get_height() + self.MENU_BAR_HEIGHT,
                )
                obj_list = (
                    self.active_keyboard_objects
                    if self.keyboard_visible
                    else self.default_objects
                )
                for obj in obj_list:
                    if obj.event(event, transformed_pos):
                        event.dict["consumed"] = True
                        continue
            if event.dict.get("consumed"):
                continue

            # Handle clicks on screen objects
            screen.event(event)

            if event.type == pygame.KEYDOWN and (
                active_object := ScreenManager.instance.active_object
            ):
                active_object.key_event(event)

    @property
    def keyboard_visible(self):
        if self.active_object:
            return self.active_object.keyboard_settings["enabled"]
        return False
