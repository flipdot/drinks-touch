import pygame

from elements.base_elm import BaseElm


class HBox(BaseElm):

    def __init__(
        self,
        children: list["BaseElm"] | None = None,
        gap=5,
        pos=(0, 0),
        *args,
        **kwargs,
    ):
        super().__init__(children, pos, 0, 0, *args, **kwargs)
        self.pos = pos
        self.gap = gap

    def render(self, *args, **kwargs) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        x = self.padding_left
        for element in self.children:
            element.pos = (x, self.padding_top)
            element_surface = element.render(*args, **kwargs)
            surface.blit(element_surface, element.pos)
            x += element.width + self.gap
        return surface

    @property
    def width(self):
        return (
            sum([element.width for element in self.children])
            + (len(self.children) - 1) * self.gap
            + self.padding_left
            + self.padding_right
        )

    @property
    def height(self):
        return (
            max([element.height for element in self.children])
            + self.padding_top
            + self.padding_bottom
        )

    # def on_click(self, x, y):
    #     for obj in self.elements:
    #         if pygame.Rect(obj.box).collidepoint(x, y):
    #             if hasattr(obj, "on_click"):
    #                 obj.on_click(x - obj.pos[0], y - obj.pos[1])
    #             break

    def render_debug(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((0, 0, 255, 100))
        for element in self.children:
            element_surface = element.render_debug()
            surface.blit(element_surface, element.pos)
        pygame.draw.rect(surface, (255, 0, 0), (0, 0, self.width, self.height), 1)
        return surface
