import pygame

from .base_elm import BaseElm


class Label(BaseElm):
    _font_cache = {}

    def __init__(self, screen, **kwargs):
        self.font_face = kwargs.get('font', 'sans serif')
        self.size = kwargs.get('size', 50)
        self.max_width = kwargs.get('max_width', None)
        # if True, pos marks top-right instead of top-left corner
        self.align_right = kwargs.get('align_right', False)
        self.text = kwargs.get('text', '<Label>')
        self.color = kwargs.get('color', (246, 198, 0))

        pos = kwargs.get('pos', (0, 0))
        super(Label, self).__init__(screen, pos, self.size, -1)

        self.font = Label.get_font(self.font_face, self.size)

    @classmethod
    def get_font(cls, font_face, size):
        if (font_face, size) not in cls._font_cache:
            font = pygame.font.SysFont(font_face, size)
            cls._font_cache[(font_face, size)] = font
        return cls._font_cache[(font_face, size)]

    def render(self):
        elm = self.font.render(self.text, 1, self.color)
        cutx = 0
        pos = self.pos
        if self.align_right:
            if self.max_width:
                align_width = min(self.max_width, elm.get_width())
                cutx = max(0, elm.get_width() - self.max_width)
            else:
                align_width = elm.get_width()
            pos = (self.pos[0] - align_width, self.pos[1])

        area = pygame.Rect(
            cutx,
            0,
            self.max_width if self.max_width else elm.get_width(),
            elm.get_height()
        )

        self.screen.blit(elm, pos, area)
