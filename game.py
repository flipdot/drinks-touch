import pygame
from pygame.locals import *
from screen import get_screen

screen = get_screen()

done = False
screen.fill((0, 0, 0))
other1 = pygame.image.load("img/test.jpg").convert_alpha()
other2 = pygame.transform.rotate(other1, 270)
screen.blit(other2, (0, 0))
pygame.display.flip()

while not done:
    for e in pygame.event.get():
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            done = True
            break
