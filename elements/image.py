import pygame

from .base_elm import BaseElm

class Image(BaseElm):
    def __init__(self, screen, **kwargs):
        self.pos = kwargs.get('pos', (0, 0))
        self.src = kwargs.get('src', 'img/test.jpg')

        self.__load_img()

        pos = kwargs.get('pos', (0, 0))
        img_size = self.img.get_size()
        super(Image, self).__init__(screen, pos, img_size[1], img_size[0])

    def __load_img(self):
        self.img = pygame.image.load(self.src).convert_alpha()

    def render(self):
        self.screen.blit(self.img, self.pos)
