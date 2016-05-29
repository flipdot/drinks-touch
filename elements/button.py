import pygame

from .base_elm import BaseElm

class Button(BaseElm):
    def __init__(self, screen, **kwargs):
        self.font = kwargs.get('font', 'monospace')
        self.size = kwargs.get('size', 30)
        self.text = kwargs.get('text', '<Label>')
        self.color = kwargs.get('color', (246, 198, 0))
        self.clicked = kwargs.get('click', self.__clicked)
        self.click_param = kwargs.get('click_param', None)

        pos = kwargs.get('pos', (0, 0))
        super(Button, self).__init__(screen, pos, self.size, -1)

        self.__load_font()

    def __load_font(self):
        self.font = pygame.font.SysFont(self.font, self.size)

    def __clicked(self, param, pos):
        print "Clicked on button without handler"

    def render(self):
        elm = self.font.render(self.text, 1, self.color)
        self.screen.blit(elm, self.pos)

        padding = 10
        self.box = (
            self.pos[0]-padding,
            self.pos[1]-padding,
            elm.get_width()+padding*2,
            elm.get_height()+padding*2
        )

        pygame.draw.rect(
            self.screen,
            self.color,
            self.box,
            1
        )

    def events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if pygame.Rect(self.box).collidepoint(pos):
                    self.clicked(self.click_param, pos)
