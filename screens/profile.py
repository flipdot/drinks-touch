# coding=utf-8
from decimal import getcontext

import pygame
import datetime

from elements.label import Label
from elements.button import Button
from elements.image import Image
from elements.progress import Progress

from drinks.drinks_manager import DrinksManager
from drinks.drinks import get_by_ean

from users.users import Users

from .screen import Screen
from .success import SuccessScreen
from .id_card_screen import IDCardScreen

from database.storage import get_session
from database.models.scan_event import ScanEvent
from sqlalchemy.sql import text

from .screen_manager import ScreenManager

from env import monospace

class ProfileScreen(Screen):
    def __init__(self, screen, user, **kwargs):
        super(ProfileScreen, self).__init__(screen)

        self.user = user

        self.objects.append(Button(
            self.screen,
            text = "BACK",
            pos=(30,30),
            font = monospace,
            click=self.back
        ))

        self.objects.append(Button(
            self.screen,
            text = "ID card",
            pos=(340,30),
            font = monospace,
            click=self.id_card
        ))

        self.objects.append(Label(
            self.screen,
            text =self.user["name"],
            pos=(30, 120),
            size=70,
            max_width=335 - 30 - 10,  # balance.x - self.x - margin
        ))

        self.objects.append(Label(
            self.screen,
            text = 'Guthaben',
            pos=(330, 120),
            size=30
        ))

        self.label_verbrauch = Label(
            self.screen,
            text='Bisheriger Verbrauch:',
            pos=(30, 180),
            size=30
        )
        self.label_aufladungen = Label(
            self.screen,
            text='Aufladungen:',
            pos=(30, 180),
            size=30
        )

        self.processing = Label(
            self.screen,
            text="Moment bitte...",
            size=40,
            pos=(150, 750)
        )
        self.processing.is_visible = False
        self.objects.append(self.processing)

        self.timeout = Progress(
            self.screen,
            pos=(200, 50),
            speed=1/30.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        drink = DrinksManager.get_instance().get_selected_drink()
        self.drink_info = Label(
            self.screen,
            text=drink['name'] if drink else "",
            size=60,
            pos=(30, 630)
        )

        self.zuordnen = Button(
            self.screen,
            text='Trinken',
            pos=(30, 690),
            size=50,
            click=self.save_drink
        )
        self.btn_aufladungen = Button(
            self.screen,
            text='Aufladungen',
            pos=(30, 700),
            click=self.show_aufladungen
        )
        self.btn_drinks = Button(
            self.screen,
            text='Buchungen',
            pos=(30, 700),
            click=self.show_drinks
        )
        self.elements_aufladungen = [self.btn_drinks, self.label_aufladungen]
        self.elements_drinks = [self.label_verbrauch]
        if drink:
            self.elements_drinks.extend([self.zuordnen, self.drink_info])
        else:
            self.elements_drinks.append(self.btn_aufladungen)

        self.objects.append(Button(
            self.screen,
            text='Abbrechen',
            pos=(290, 700),
            size=30,
            click=self.btn_home,
        ))

        balance = Users.get_balance(self.user['id'])
        self.objects.append(Label(
            self.screen,
            text = str(balance),
            pos=(335, 145),
            size=40
        ))

        drinks = self.get_stats()
        for i, drinks in enumerate(drinks):
            x = 30
            if i == 11:
                self.elements_drinks.append(Label(
                    self.screen,
                    text = "...",
                    pos=(x, 210 + (i * 35))
                ))
                continue
            if i > 11:
                continue
            text = get_by_ean(drinks["name"])['name']
            count_width = 80
            margin_right = 10
            self.elements_drinks.append(Label(
                self.screen,
                text = text,
                pos=(x, 210 + (i * 35)),
                max_width=480-x-margin_right-count_width
            ))
            self.elements_drinks.append(Label(
                self.screen,
                text = str(drinks["count"]),
                align_right=True,
                pos=(480-margin_right, 210 + (i * 35)),
                max_width=count_width
            ))

        self.objects.extend(self.elements_drinks)

        aufladungen = Users.get_recharges(self.user['id'], limit=12)
        y = 210
        prev_date = None
        for i, aufladung in enumerate(aufladungen):
            x = 30
            if y + 45*2 >= self.btn_drinks.pos[1]:
                self.elements_aufladungen.append(Label(self.screen,
                    text = "...",
                    pos=(x, y)
                ))
                break
            date = aufladung.timestamp.strftime("%a, %-d.%-m.%Y")
            time = aufladung.timestamp.strftime("%H:%M")
            text = time
            helper = Users.get_by_id(
                aufladung.helper_user_id) if aufladung.helper_user_id else None
            if helper:
                text += " mit " + helper['name']
            if date != prev_date:
                prev_date = date
                self.elements_aufladungen.append(Label(self.screen,
                    text=date, size=35,
                    pos=(x, y+15)
                ))
                y += 45
            count_width = 120
            margin_right = 10
            self.elements_aufladungen.append(Label(self.screen,
                text=text,
                pos=(x + 10, y), size=45,
                max_width=480 - x - margin_right - count_width
            ))
            self.elements_aufladungen.append(Label(
                self.screen,
                text = str(aufladung.amount),
                align_right=True,
                pos=(480-margin_right, y-5),
                max_width=count_width
            ))
            y += 35

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
            DrinksManager.get_instance().set_selected_drink(None)
            Users.delete_if_nomoney(self.user)
        else:
            drink = {}

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(SuccessScreen(self.screen, self.user, drink, session))

    def on_barcode(self, barcode):
        if not barcode:
            return
        self.processing.is_visible = True
        user = Users.get_by_id_card(barcode)
        if user:
            ScreenManager.get_instance().set_active(
                ProfileScreen(self.screen, user)
            )
            self.processing.is_visible = False
            return
        drink = get_by_ean(barcode)
        DrinksManager.get_instance().set_selected_drink(drink)
        self.drink_info.text = drink['name']
        if self.zuordnen not in self.objects:
            self.objects.extend([self.zuordnen, self.drink_info])
        self.processing.is_visible = False
        self.timeout.start()

    def back(self, param, pos):
        screen_manager = ScreenManager.get_instance()
        screen_manager.go_back()

    def id_card(self, params, pos):
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(IDCardScreen(self.screen, self.user))

    def home(self):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def btn_home(self, param, pos):
        self.home()

    def time_elapsed(self):
        self.home()

    def show_aufladungen(self, param, pos):
        for d in self.elements_drinks:
            self.objects.remove(d)
        self.objects.extend(self.elements_aufladungen)
        self.timeout.start()

    def show_drinks(self, param, pos):
        for d in self.elements_aufladungen:
            self.objects.remove(d)
        self.objects.extend(self.elements_drinks)
        self.timeout.start()

    def get_stats(self):
        session = get_session()
        sql = text("""
            SELECT COUNT(*) as count, barcode as name
            FROM scanevent
            WHERE user_id = :userid
            GROUP BY barcode
            ORDER by count DESC
        """)
        userid=self.user['id']
        result = session.connection().execute(sql, userid=userid).fetchall()

        return result