import enum
import functools

import pygame
from pygame.event import EventType

from elements import Label, Button
from elements.base_elm import BaseElm
from elements.hbox import HBox
from elements.vbox import VBox
from overlays import BaseOverlay
from screens.screen_manager import ScreenManager


class KeyboardLayout(enum.Enum):
    DEFAULT = "default"
    NUMERIC = "numeric"


class KeyboardOverlay(BaseOverlay):
    ANIMATION_DURATION = 0.2

    def __init__(self, screen_manager: ScreenManager):
        super().__init__(screen_manager)
        self.width = self.screen.get_width()
        self.height = 350
        self.pos = pygame.Vector2(
            0,
            self.screen.get_height()
            - self.height
            - self.screen_manager.MENU_BAR_HEIGHT,
        )
        self._layout_override = None

        self._anim_start_pos = pygame.Vector2(
            0, self.screen.get_height() - self.height * 0.9
        )

        num_btn_size = 50

        def make_num_btn(n: str):
            return Button(
                text=f" {n} ",
                size=num_btn_size,
                on_click=functools.partial(
                    self.press_key, getattr(pygame, f"K_{n}"), n
                ),
            )

        self.layouts: dict[KeyboardLayout, list[BaseElm]] = {
            KeyboardLayout.DEFAULT: [
                Label(
                    text="Keyboard (default layout)",
                    pos=(0, 0),
                ),
                Button(
                    text="123",
                    pos=(0, self.height - 75),
                    size=40,
                    on_click=functools.partial(self.set_layout, KeyboardLayout.NUMERIC),
                ),
            ],
            KeyboardLayout.NUMERIC: [
                VBox(
                    [
                        HBox(
                            [
                                make_num_btn("1"),
                                make_num_btn("2"),
                                make_num_btn("3"),
                                Button(
                                    text=" ← ",
                                    size=num_btn_size,
                                    on_click=functools.partial(
                                        self.press_key, pygame.K_BACKSPACE
                                    ),
                                ),
                            ]
                        ),
                        HBox(
                            [
                                make_num_btn("4"),
                                make_num_btn("5"),
                                make_num_btn("6"),
                            ]
                        ),
                        HBox(
                            [
                                make_num_btn("7"),
                                make_num_btn("8"),
                                make_num_btn("9"),
                            ]
                        ),
                        HBox(
                            [
                                Button(
                                    text=" - ",
                                    size=num_btn_size,
                                    on_click=functools.partial(
                                        self.press_key, pygame.K_MINUS, "-"
                                    ),
                                ),
                                make_num_btn("0"),
                                Button(
                                    text=" . ",
                                    size=num_btn_size,
                                    on_click=functools.partial(
                                        self.press_key, pygame.K_PERIOD, "."
                                    ),
                                ),
                                Button(
                                    text="abc",
                                    size=num_btn_size,
                                    on_click=functools.partial(
                                        self.set_layout, KeyboardLayout.DEFAULT
                                    ),
                                ),
                            ]
                        ),
                    ],
                    pos=(0, 0),
                    padding=10,
                ),
            ],
        }
        self.clock = 0

    def press_key(self, key: int, char: str | None = None):
        event = pygame.event.Event(pygame.KEYDOWN, key=key, unicode=char)
        self.screen_manager.events([event])

    def render(self, dt):
        if not self.visible:
            self.clock = 0
            return
        self.clock += dt
        surface = pygame.Surface(
            (self.screen.get_width(), self.height), pygame.SRCALPHA
        )
        surface.fill((0, 0, 0, 255))

        for obj in self.layout:
            obj_surface = obj.render(dt)
            if obj_surface is not None:
                surface.blit(obj_surface, obj.screen_pos)

        # full alpha (255) after ANIMATION_DURATION
        alpha = min(255, int((self.clock / self.ANIMATION_DURATION) * 255))
        surface.set_alpha(alpha)

        # self.pos after ANIMATION_DURATION, interpolate
        # from self._anim_start_pos to self.pos
        if self.clock < self.ANIMATION_DURATION:
            pos = self._anim_start_pos.lerp(
                self.pos, self.clock / self.ANIMATION_DURATION
            )
        else:
            pos = self.pos

        self.screen.blit(surface, pos)

    def events(self, events: list[EventType]):
        if not self.visible:
            self.set_layout(None)
            return False
        # check if click is inside keyboard
        for event in events:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                or event.type == pygame.MOUSEBUTTONUP
            ):
                transformed_pos = (
                    event.pos[0] - self.pos[0],
                    event.pos[1] - self.pos[1],
                )
                if self.collides_with(transformed_pos):
                    event.dict["consumed"] = True
                    for obj in self.layout:
                        if obj.event(event, transformed_pos):
                            continue

    def collides_with(self, pos: tuple[float, float]) -> bool:
        return pygame.Rect(0, 0, self.width, self.height).collidepoint(pos[0], pos[1])

    @property
    def visible(self):
        if obj := self.screen_manager.active_object:
            return obj.keyboard_settings["enabled"]

    @property
    def settings(self):
        return self.screen_manager.active_object.keyboard_settings

    @property
    def layout(self):
        if self._layout_override:
            return self.layouts[self._layout_override]
        return self.layouts[self.settings["layout"]]

    def set_layout(self, layout: KeyboardLayout | None):
        self._layout_override = layout
