# coding=utf-8
import pygame

from elements.label import Label
from elements.button import Button

from .screen import Screen

class NamesScreen(Screen):
    def __init__(self, screen, char, **kwargs):
        super(NamesScreen, self).__init__(screen)

        self.char = char

        self.objects.append(Button(
            self.screen,
            text = "BACK",
            pos=(30,30),
            color = (255, 255, 0),
            click=self.back
        ))

        self.objects.append(Label(
            self.screen,
            text ='Wer bist du?',
            pos=(20, 130),
            color = (255, 255, 0),
        ))

        self.objects.append(Button(
            self.screen,
            text = 'Gast ('+str(self.char)+')',
            pos=(30,190),
            color = (255, 255, 0)
        ))

    def back(self, param, pos):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()
