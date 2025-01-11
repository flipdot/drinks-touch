import enum
import functools

import pygame
from pygame.event import EventType

from elements import Button
from elements.base_elm import BaseElm
from elements.hbox import HBox
from elements.spacer import Spacer
from elements.vbox import VBox
from overlays import BaseOverlay

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens.screen_manager import ScreenManager


class KeyboardLayout(enum.Enum):
    DEFAULT = "default"
    CAPS = "caps"
    NUMERIC = "numeric"


class KeyboardOverlay(BaseOverlay):
    ANIMATION_DURATION = 0.2
    instance = None

    def __init__(self, screen_manager: "ScreenManager"):
        assert KeyboardOverlay.instance is None, "KeyboardOverlay is a singleton"
        super().__init__(screen_manager)
        self.width = self.screen.get_width()
        self.height = 350
        self.pos = pygame.Vector2(
            0,
            self.screen.get_height()
            - self.height
            - self.screen_manager.MENU_BAR_HEIGHT,
        )

        self._anim_start_pos = pygame.Vector2(
            0, self.screen.get_height() - self.height * 0.9
        )

        num_btn_size = 50
        KeyboardOverlay.instance = self

        def make_num_btn(n: str):
            return Button(
                text=f" {n} ",
                size=num_btn_size,
                on_click=functools.partial(
                    self.press_key, getattr(pygame, f"K_{n}"), n
                ),
            )

        def key_btn(c: str):
            keycode = getattr(pygame, f"K_{c.lower()}")
            return Button(
                text=f" {c} ",
                size=23,
                padding=(15, 0, 15),
                on_click=functools.partial(self.press_key, keycode, c),
            )

        self.layouts: dict[KeyboardLayout, list[BaseElm]] = {
            KeyboardLayout.DEFAULT: [
                VBox(
                    [
                        HBox(
                            [
                                key_btn("1"),
                                key_btn("2"),
                                key_btn("3"),
                                key_btn("4"),
                                key_btn("5"),
                                key_btn("6"),
                                key_btn("7"),
                                key_btn("8"),
                                key_btn("9"),
                                key_btn("0"),
                            ]
                        ),
                        HBox(
                            [
                                key_btn("q"),
                                key_btn("w"),
                                key_btn("e"),
                                key_btn("r"),
                                key_btn("t"),
                                key_btn("z"),
                                key_btn("u"),
                                key_btn("i"),
                                key_btn("o"),
                                key_btn("p"),
                            ]
                        ),
                        HBox(
                            [
                                Spacer(width=15),
                                key_btn("a"),
                                key_btn("s"),
                                key_btn("d"),
                                key_btn("f"),
                                key_btn("g"),
                                key_btn("h"),
                                key_btn("j"),
                                key_btn("k"),
                                key_btn("l"),
                            ]
                        ),
                        HBox(
                            [
                                Button(
                                    text=" ⇧ ",
                                    size=23,
                                    padding=(15, 0, 15),
                                    on_click=functools.partial(
                                        self.set_layout, KeyboardLayout.CAPS
                                    ),
                                ),
                                key_btn("y"),
                                key_btn("x"),
                                key_btn("c"),
                                key_btn("v"),
                                key_btn("b"),
                                key_btn("n"),
                                key_btn("m"),
                                Button(
                                    text=" ← ",
                                    size=23,
                                    padding=15,
                                    on_click=functools.partial(
                                        self.press_key, pygame.K_BACKSPACE
                                    ),
                                ),
                            ]
                        ),
                        row_spacebar := HBox(
                            [
                                Button(
                                    text="123",
                                    size=23,
                                    padding=15,
                                    on_click=functools.partial(
                                        self.set_layout, KeyboardLayout.NUMERIC
                                    ),
                                ),
                                Spacer(width=58),
                                Button(
                                    text=" ",
                                    size=23,
                                    padding=(15, 86, 15),
                                    on_click=functools.partial(
                                        self.press_key, pygame.K_SPACE, " "
                                    ),
                                ),
                            ]
                        ),
                    ],
                    pos=(0, 0),
                    padding=10,
                ),
            ],
            KeyboardLayout.CAPS: [
                VBox(
                    [
                        HBox(
                            [
                                key_btn("1"),
                                key_btn("2"),
                                key_btn("3"),
                                key_btn("4"),
                                key_btn("5"),
                                key_btn("6"),
                                key_btn("7"),
                                key_btn("8"),
                                key_btn("9"),
                                key_btn("0"),
                            ]
                        ),
                        HBox(
                            [
                                key_btn("Q"),
                                key_btn("W"),
                                key_btn("E"),
                                key_btn("R"),
                                key_btn("T"),
                                key_btn("Z"),
                                key_btn("U"),
                                key_btn("I"),
                                key_btn("O"),
                                key_btn("P"),
                            ]
                        ),
                        HBox(
                            [
                                Spacer(width=15),
                                key_btn("A"),
                                key_btn("S"),
                                key_btn("D"),
                                key_btn("F"),
                                key_btn("G"),
                                key_btn("H"),
                                key_btn("J"),
                                key_btn("K"),
                                key_btn("L"),
                            ]
                        ),
                        HBox(
                            [
                                Button(
                                    text=" ⇧ ",
                                    size=23,
                                    padding=(15, 0, 15),
                                    on_click=functools.partial(
                                        self.set_layout, KeyboardLayout.DEFAULT
                                    ),
                                ),
                                key_btn("Y"),
                                key_btn("X"),
                                key_btn("C"),
                                key_btn("V"),
                                key_btn("B"),
                                key_btn("N"),
                                key_btn("M"),
                                Button(
                                    text=" ← ",
                                    size=23,
                                    padding=15,
                                    on_click=functools.partial(
                                        self.press_key, pygame.K_BACKSPACE
                                    ),
                                ),
                            ]
                        ),
                        row_spacebar,
                    ],
                    pos=(0, 0),
                    padding=10,
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
        self.layout = self.layouts[KeyboardLayout.DEFAULT]
        self.clock = 0
        self._settings_for_object = None

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

    def apply_settings(self, settings: dict):
        self.layout = self.layouts[settings.get("layout", KeyboardLayout.DEFAULT)]

    def set_layout(self, layout: KeyboardLayout | None):
        self.layout = self.layouts[layout]
