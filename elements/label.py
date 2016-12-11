import pygame

from .base_elm import BaseElm

class Label(BaseElm):
    def __init__(self, screen, **kwargs):
        self.font = kwargs.get('font', 'sans serif')
        self.size = kwargs.get('size', 50)
        self.max_width = kwargs.get('max_width', None)
        self.text = kwargs.get('text', '<Label>')
        self.color = kwargs.get('color', (246, 198, 0))

        pos = kwargs.get('pos', (0, 0))
        super(Label, self).__init__(screen, pos, self.size, -1)

        self.__load_font()

    def __load_font(self):
        self.font = pygame.font.SysFont(self.font, self.size)

    def render(self, t, dt):
        elm = self.font.render(self.text, 1, self.color)
        area = pygame.Rect(0,0,
            self.max_width if self.max_width else elm.get_width(),
            elm.get_height()
        )
        self.screen.blit(elm, self.pos, area)
