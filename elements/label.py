import pygame

class Label:
    def __init__(self, screen, **kwargs):
        self.screen = screen
        self.font = kwargs.get('font', 'monospace')
        self.size = kwargs.get('size', 25)
        self.text = kwargs.get('text', '<Label>')
        self.color = kwargs.get('color', (255, 255, 255))
        self.pos = kwargs.get('pos', (0, 0))

        self.__load_font()

    def __load_font(self):
        self.font = pygame.font.SysFont(self.font, self.size)

    def render(self):
        elm = self.font.render(self.text, 1, self.color)
        self.screen.blit(elm, self.pos)
