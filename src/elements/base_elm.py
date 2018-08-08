import pygame

class BaseElm(object):
    def __init__(self, screen, pos, height, width):
        self.screen = screen
        self.pos = pos
        self.height = height
        self.width = width
        self.is_visible = True

    def events(self, events):
        pass

    def visible(self):
        return self.is_visible