# coding=utf-8
import pygame

from elements.label import Label
from elements.button import Button

from .screen import Screen

class MainScreen(Screen):
    def __init__(self, screen, **kwargs):
        super(MainScreen, self).__init__(screen)

        self.objects.append(Label(
            self.screen,
            text = u'flipdot getränke-scanner',
            pos = (20, 20),
            color = (255, 255, 0)
        ))

        self.objects.append(Label(
            self.screen,
            text = u'Alles neu, geil!',
            pos = (60, 60),
            color = (255, 255, 0)
        ))

        self.objects.append(Button(
            self.screen,
            text = u'Klick mich!',
            pos=(100, 150),
            color = (255, 255, 0)
        ))
