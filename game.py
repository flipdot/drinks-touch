 # coding=utf-8
import pygame
from pygame.locals import *

from screen import get_screen

from elements.label import Label
from elements.image import Image

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
