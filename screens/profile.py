# coding=utf-8
import pygame

from elements.label import Label
from elements.button import Button
from elements.image import Image

from users.users import Users

from .screen import Screen

class ProfileScreen(Screen):
    def __init__(self, screen, user, **kwargs):
        super(ProfileScreen, self).__init__(screen)

        self.user = user

        self.objects.append(Button(
            self.screen,
            text = "HOME",
            pos=(30,30),
            font = "monospace",
            click=self.back,
            size=30
        ))

        self.objects.append(Label(
            self.screen,
            text =self.user["name"],
            pos=(30, 120),
            size=70
        ))

        self.objects.append(Label(
            self.screen,
            text = u"Scanne dein Getränk!",
            pos=(30, 170),
        ))

        self.objects.append(Image(
            self.screen,
            src = "img/chart.png",
            pos=(30, 235),
        ))        

        filters = [
            {
                "name": "Heute", 
                "key": "today"
            },
            {
                "name": "Woche", 
                "key": "week"
            },
            {
                "name": "Monat", 
                "key": "month"
            },
            {
                "name": "Insg.", 
                "key": "total"
            }
        ]

        i = 0
        for filter in filters:
            x = 30 + (i * 115)
            self.objects.append(Button(
                self.screen,
                text = filter["name"],
                pos=(x, 550),
                font="monospace",
                size=30
            ))   

            i += 1     

        i = 0
        for drinks in self.user["drinks"]:
            text = drinks["name"] + ": " + str(drinks["count"])
            self.objects.append(Label(
                self.screen,
                text = text,
                pos=(30,620 + (i * 35)),
            ))
            i += 1

    def back(self, param, pos):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()
