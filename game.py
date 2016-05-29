#!/usr/bin/env python
# coding=utf-8
import pygame
import logging

logging.basicConfig(level=logging.DEBUG)

from threading import Thread

from pygame.locals import *
from screen import get_screen
from screens.screen_manager import ScreenManager


from drinks_log.log import Log as DrinksLog

from webserver.webserver import run as run_webserver


screen = get_screen()
screen_manager = ScreenManager(screen)
ScreenManager.set_instance(screen_manager)


##### Drinks log #####

def append_label(text):
    print text

log = DrinksLog()
log.register_handler(append_label)

webserver_thread = Thread(
    target=run_webserver,
    args=(log,)
)
webserver_thread.daemon = True
webserver_thread.start()

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
