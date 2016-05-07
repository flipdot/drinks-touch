 # coding=utf-8
import pygame
from threading import Thread

from pygame.locals import *
from screen import get_screen

from elements.label import Label
from elements.image import Image
from drinks_log.log import Log as DrinksLog

from webserver.webserver import run as run_webserver


screen = get_screen()
objects = []

objects.append(Label(
    screen,
    text = u'flipdot getränke-scanner',
    pos = (20, 20),
    color = (255, 255, 0)
))

objects.append(Label(
    screen,
    text = u'Alles neu, geil!',
    pos = (60, 60),
    color = (255, 255, 0)
))

objects.append(Image(
    screen,
    pos=(100, 100)
))

##### Drinks log #####

drinks_vars = {}

drinks_vars['log_last_pos'] = 150
def append_label(text):
    size = 10
    objects.append(Label(
        screen,
        text=text,
        size=size,
        color=(255, 255, 0),
        pos=(20, drinks_vars['log_last_pos'])
    ))
    drinks_vars['log_last_pos'] += size + 5

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

    for o in objects:
        o.render()

    pygame.display.flip()

    for e in pygame.event.get():
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            done = True
            break
