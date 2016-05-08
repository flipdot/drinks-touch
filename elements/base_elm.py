import pygame

class BaseElm(object):
    def __init__(self, screen, pos, height, width):
        self.screen = screen
        self.pos = pos
        self.height = height
        self.width = width
