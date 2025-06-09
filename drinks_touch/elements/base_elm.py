from __future__ import annotations
import pygame
from pygame import Surface


class BaseElm:
    def __init__(
        self,
        children: list["BaseElm"] | None = None,
        pos=None,
        height=None,
        width=None,
        align_right=False,
        align_bottom=False,
        visible=True,
        padding: (
            int | tuple[int, int] | tuple[int, int, int] | tuple[int, int, int, int]
        ) = 0,
    ):
        if pos is None:
            pos = (0, 0)
        self.ts_active = 0
        self.pos = pos
        self._height = height
        self._width = width
        self.visible = visible
        self.align_right = align_right
        self.align_bottom = align_bottom
        self.focus = False
        if children is None:
            children = []
        self.children = children
        self.clickable = hasattr(self, "on_click")
        self.dirty = True
        self.last_hash = 0
        self.surface: Surface | None = None
        self.overlay_surface: Surface | None = None
        for child in children:
            if child.clickable:
                self.clickable = True
                break
        if not isinstance(padding, tuple):
            self.padding_top = padding
            self.padding_right = padding
            self.padding_bottom = padding
            self.padding_left = padding
        elif len(padding) == 2:
            self.padding_top = padding[0]
            self.padding_right = padding[1]
            self.padding_bottom = padding[0]
            self.padding_left = padding[1]
        elif len(padding) == 3:
            self.padding_top = padding[0]
            self.padding_right = padding[1]
            self.padding_bottom = padding[2]
            self.padding_left = padding[1]
        else:
            self.padding_top = padding[0]
            self.padding_right = padding[1]
            self.padding_bottom = padding[2]
            self.padding_left = padding[3]

    def calculate_hash(self):
        """
        Calculate a hash based on the element's properties.
        This can be used to determine if the element has changed.
        """
        return hash(
            (
                tuple(self.pos),  # could be a vector, which is unhashable
                self._height,
                self._width,
                self.visible,
                self.screen_pos,
                self.padding_top,
                self.padding_right,
                self.padding_bottom,
                self.padding_left,
                tuple(child.calculate_hash() for child in self.children),
            )
        )

    @property
    def keyboard_settings(self):
        return {
            "enabled": False,
        }

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def screen_pos(self):
        x, y = self.pos
        if self.align_right:
            x -= self.width
        if self.align_bottom:
            y -= self.height
        return x, y

    @property
    def box(self):
        return self.screen_pos + (self.width, self.height)

    def tick(self, dt: float):
        """
        Called every frame to update the element.
        May be used to update animations or other time-based changes.
        Keep the computation simple to avoid performance issues.
        """
        for child in self.children:
            child.tick(dt)

    def event(self, event: pygame.event.Event, pos=None) -> bool:
        """
        Returns the element that consumed the event
        """
        if not self.clickable:
            return False
        if pos is None and hasattr(event, "pos"):
            pos = event.pos
        if pos is None:
            return False
        collides = self.collides_with(pos)
        transformed_pos = (
            pos[0] - self.screen_pos[0],
            pos[1] - self.screen_pos[1],
        )

        for child in self.children:
            if child.event(event, transformed_pos):
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if collides:
                self.focus = True
                return True
            else:
                self.focus = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

            had_focus = self.focus
            self.focus = False
            if had_focus and collides:
                if hasattr(self, "on_click"):
                    self.on_click(*transformed_pos)
                return True

        return False

    def key_event(self, event: pygame.event.Event):
        """
        Called when a keyboard key was pressed and the element is active
        (active means: was clicked on before and therefore the ScreenManager
        has set this element as active)
        """

    def collides_with(self, pos: tuple[float, float]) -> bool:
        return (
            self.box is not None
            and self.visible
            and pygame.Rect(self.box).collidepoint(pos[0], pos[1])
        )

    def render(self, *args, **kwargs) -> Surface | None:
        surface = pygame.font.SysFont("monospace", 25).render(
            "Return surface or None in render()", 1, (255, 0, 255)
        )
        return surface

    def render_overlay(self, *args, **kwargs) -> Surface | None:
        return None

    def render_cached(self, *args, **kwargs):
        if self.last_hash != (new_hash := self.calculate_hash()):
            self.dirty = True
            self.last_hash = new_hash
        if self.dirty:
            self.surface = self.render(*args, **kwargs)
            self.overlay_surface = self.render_overlay(*args, **kwargs)
            self.dirty = False

    def render_debug(self) -> pygame.Surface:
        w = self.width
        h = self.height
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 255), (0, 0, w, h), 1)
        pygame.draw.line(surface, (255, 0, 255), (0, 0), (w, h))
        pygame.draw.line(surface, (255, 0, 255), (0, h), (w, 0))
        return surface
