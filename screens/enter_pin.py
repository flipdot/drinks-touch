# coding=utf-8
import pygame

from elements.label import Label
from elements.button import Button

from users.users import Users

from .screen import Screen
from screens.profile import ProfileScreen

class EnterPinScreen(Screen):
    def __init__(self, screen, user, **kwargs):
        super(EnterPinScreen, self).__init__(screen)
        self.user = user

        self.objects.append(Button(
            self.screen,
            text = "BACK",
            pos=(30,30),
            click=self.back,
            font = "monospace",
            size=30
        ))

        self.objects.append(Button(
            self.screen,
            text = "UNLOCK!",
            pos=(110, 700),
            click=self.btn_ok,
            font = "monospace",
            size=80
        ))

        self.objects.append(Label(
            self.screen,
            text ='/s Barcode oder /e PIN:',
            pos=(20, 130),
        ))        

        self.input = Label(
            self.screen,
            text = '_',
            pos=(100, 200),
        )
        self.objects.append(self.input)

        keys = [
            [ '1', '2', '3' ],
            [ '4', '5', '6' ],
            [ '7', '8', '9' ],
            [ '#', '0', '*' ]
        ]

        x = 0
        y = 0
        for row in keys:
            for label in row:
                self.render_digit_btn(label, x, y)
                x += 1
            x = 0
            y += 1

        self.objects.append(Button(
            self.screen,
            text = 'DEL',
            pos=(200, 560),
            font = "monospace",
            click=self.del_char,
            size=60
        ))

    def render_digit_btn(self, label, x, y):
        cord_x = 160 + x  * 70
        cord_y = 280 + y  * 70
        self.objects.append(Button(
            self.screen,
            text = label,
            pos=(cord_x, cord_y),
            click=self.add_char,
            click_param=label,
            font = "monospace",
            size=60
        ))

        print (cord_x, cord_y)

    def add_char(self, param, pos):
        self.input.text = self.input.text.split('_')[0] + param
        self.input.text += '_'

    def del_char(self, param, pos):
        self.input.text = self.input.text[:len(self.input.text)-2]
        self.input.text += '_'        

    def btn_ok(self, param, pos):
        # TODO check the pin using
        # self.get_pin() and self.user

        from .screen_manager import ScreenManager
        ScreenManager.get_instance().set_active(
            ProfileScreen(self.screen, self.user)
        )

    def get_pin(self):
        return self.input.text[:len(self.input.text)-1]

    def back(self, param, pos):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.go_back()

    def switch_to_screen(self, param, pos):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(
            ProfileScreen(self.screen, param)
        )

    def on_barcode(self, barcode):
        for c in barcode:
            self.add_char(c, null)