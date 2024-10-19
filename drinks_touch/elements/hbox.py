import pygame

from elements.base_elm import BaseElm


class HBox(BaseElm):

    def __init__(self, screen, elements: list[BaseElm], gap=5, pos=(0, 0), **kwargs):
        super().__init__(screen, pos, 0, 0)
        self.screen = screen
        self.pos = pos
        self.elements = elements
        self.gap = gap

    def render(self, *args, **kwargs) -> pygame.Surface:
        x = self.pos[0]
        for element in self.elements:
            element.pos = (x, self.pos[1])
            element.render(*args, **kwargs)
            x += element.width + self.gap
        self.height = max([element.height for element in self.elements])
        self.width = x - self.pos[0] - self.gap
        return super().render()
