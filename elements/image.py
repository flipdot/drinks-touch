import pygame

class Image:
    def __init__(self, screen, **kwargs):
        self.screen = screen
        self.pos = kwargs.get('pos', (0, 0))
        self.src = kwargs.get('src', 'img/test.jpg')

        self.__load_img()

    def __load_img(self):
        self.img = pygame.image.load(self.src).convert_alpha()

    def render(self):
        self.screen.blit(self.img, self.pos)
