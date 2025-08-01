import pygame
from pygame import Surface

import config
from config import Color
from elements.base_elm import BaseElm


class VBox(BaseElm):

    def __init__(
        self,
        children: list["BaseElm"] | None = None,
        gap=5,
        pos=(0, 0),
        width=None,
        height=None,
        *args,
        **kwargs,
    ):
        super().__init__(children, pos, height, width, *args, **kwargs)
        if __debug__:
            for child in children:
                assert (
                    not child.align_right
                ), "Not implemented: align_right does not have an effect on an element in a VBox"
                assert (
                    not child.align_bottom
                ), "Not implemented: align_bottom does not have an effect on an element in a VBox"
        self.pos = pos
        self.gap = gap

    def _render(self, *args, **kwargs) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        y = self.padding_top
        for element in self.children:
            element.pos = (self.padding_left, y)
            y += element.height + self.gap
            if not element.visible:
                continue
            element_surface = element._render(*args, **kwargs)
            if element_surface:
                surface.blit(element_surface, element.pos)
        if self.focus:
            pygame.draw.rect(
                surface, Color.PRIMARY.value, (0, 0, self.width, self.height), 1
            )
        return surface

    def _render_overlay(self, *args, **kwargs) -> Surface | None:
        surface = None
        y = self.padding_top
        for element in self.children:
            element.pos = (self.padding_left, y)
            element_surface = element._render_overlay(*args, **kwargs)
            if element_surface:
                if surface is None:
                    surface = pygame.Surface(
                        (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA
                    )
                surface.blit(element_surface, element.pos)
            y += element.height + self.gap
        return surface

    @property
    def width(self):
        if self._width is not None:
            return self._width
        return (
            max([element.width for element in self.children])
            + self.padding_left
            + self.padding_right
        )

    @property
    def height(self):
        if self._height is not None:
            return self._height
        return (
            sum([element.height for element in self.children])
            + (len(self.children) - 1) * self.gap
            + self.padding_top
            + self.padding_bottom
        )

    def render_debug(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((0, 0, 255, 100))
        for element in self.children:
            element_surface = element.render_debug()
            surface.blit(element_surface, element.pos)
        pygame.draw.rect(surface, (255, 0, 0), (0, 0, self.width, self.height), 1)
        return surface
