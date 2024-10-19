import pygame

from elements.base_elm import BaseElm


class VBox(BaseElm):

    def __init__(self, screen, elements: list[BaseElm], gap=5, pos=(0, 0), **kwargs):
        super().__init__(screen, pos, 0, 0)
        self.screen = screen
        self.pos = pos
        self.elements = elements
        self.gap = gap

    def render(self, *args, **kwargs) -> pygame.Surface:
        y = self.pos[1]
        for element in self.elements:
            element.pos = (self.pos[0], y)
            element.render(*args, **kwargs)
            y += element.height + self.gap
        self.width = max([element.width for element in self.elements])
        self.height = y - self.pos[1] - self.gap
        return super().render()
