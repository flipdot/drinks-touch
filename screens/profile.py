# coding=utf-8
import pygame
import datetime

from elements.label import Label
from elements.button import Button
from elements.image import Image
from drinks.drinks_manager import DrinksManager
from drinks.drinks import get_by_ean

from users.users import Users

from .screen import Screen
from .success import SuccessScreen

from database.storage import get_session
from database.models.scan_event import ScanEvent
from sqlalchemy.sql import text

class ProfileScreen(Screen):
    def __init__(self, screen, user, **kwargs):
        super(ProfileScreen, self).__init__(screen)

        self.user = user

        self.objects.append(Button(
            self.screen,
            text = "BACK",
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
            text = 'Guthaben',
            pos=(330, 120),
            size=30
        ))           

        self.objects.append(Label(
            self.screen,
            text='Bisheriger Verbrauch:',
            pos=(30, 170),
            size=30
        ))  

        self.objects.append(Button(
            self.screen,
            text='Zuordnen',
            pos=(30, 600),
            size=30,
            click=self.save_drink
        ))    

        self.objects.append(Button(
            self.screen,
            text='Abbrechen',
            pos=(280, 600),
            size=30,
            click=self.btn_home,
        ))                   

        self.objects.append(Label(
            self.screen,
            text = str(Users.get_balance(self.user['id']))+' EUR',
            pos=(335, 145),
            size=40
        ))    

        i = 0
        for drinks in self.get_stats():
            text = get_by_ean(drinks["name"])['name'] + ": " + str(drinks["count"])
            self.objects.append(Label(
                self.screen,
                text = text,
                pos=(30,210 + (i * 35)),
            ))
            i += 1

    def save_drink(self, args, pos):
        session = get_session()

        drink = DrinksManager.get_instance().get_selected_drink()
        if drink:
            ev = ScanEvent(
                drink['ean'],
                self.user['id'],
                datetime.datetime.now()
            )
            
            session.add(ev)
            session.commit()
        
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(SuccessScreen(self.screen))

    def back(self, param, pos):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.go_back()

    def home(self):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def btn_home(self, param, pos):
        self.home()

    def get_stats(self):
        session = get_session()
        sql = text("""
            SELECT COUNT(*) as count, barcode as name
            FROM scanevent
            WHERE user_id = :userid
            GROUP BY barcode
        """)
        userid=self.user['id']
        result = session.connection().execute(sql, userid=userid).fetchall()

        return result