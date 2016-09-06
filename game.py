#!/usr/bin/env python2
# coding=utf-8
import pygame
import logging
import threading

logging.basicConfig(level=logging.DEBUG)

from database.storage import init_db

from pygame.locals import *
from screen import get_screen
from screens.screen_manager import ScreenManager
from drinks.drinks_manager import DrinksManager

from webserver.webserver import run as run_webserver
from barcode.barcode_reader import run as run_barcode_reader
from barcode.barcode_worker import Worker as BarcodeWorker

screen = get_screen()

drinks_manager = DrinksManager()
DrinksManager.set_instance(drinks_manager)

screen_manager = ScreenManager(screen)
ScreenManager.set_instance(screen_manager)

init_db()

##### Barcode Scanner #####

barcode_worker = BarcodeWorker()
t = threading.Thread(
    target=run_barcode_reader,
    args=(barcode_worker,)
)
t.daemon = True
t.start()

##### webserver #####
t = threading.Thread(
    target=run_webserver
)
t.daemon = True
t.start()

##### Rendering #####

done = False
while not done:
    screen.fill((0, 0, 0))

    events = pygame.event.get()

    current_screen = screen_manager.get_active()
    current_screen.render()
    current_screen.events(events)

    pygame.display.flip()

    for e in events:
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            done = True
            break
