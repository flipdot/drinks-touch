import logging
import os

import contextlib
from functools import cache

from pygame import Surface

import config

with contextlib.redirect_stdout(None):
    import pygame

logger = logging.getLogger(__name__)


class NoVideoDriverException(Exception):
    pass


@cache
def get_screen_surface() -> Surface:
    """
    Surface that is being rendered to the screen
    """
    try:
        screen = __get_screen_framebuffer()
    except NoVideoDriverException:
        screen = __get_screen_xserver()
    return screen


def __get_screen_xserver() -> Surface:
    size = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
    # https://www.pygame.org/docs/ref/display.html?highlight=set_mode#pygame.display.set_mode
    pygame.init()

    if config.FULLSCREEN:
        flags = pygame.FULLSCREEN | pygame.NOFRAME
    else:
        flags = 0
    pygame.display.set_caption("Drinks Touch")
    screen = pygame.display.set_mode(size, flags)
    logger.info("Got regular xserver screen")
    # raise "X11 init failed"
    return screen


def __get_screen_framebuffer() -> Surface:
    # Ininitializes a new pygame screen using the framebuffer
    # Based on "Python GUI in Linux frame buffer"
    # http://www.karoltomala.com/blog/?p=679
    disp_no = os.getenv("DISPLAY")
    if disp_no:
        logger.info("I'm running under X display = {0}".format(disp_no))

    # Check which frame buffer drivers are available
    # Start with fbcon since directfb hangs with composite output
    drivers = ["wayland", "fbcon", "directfb", "svgalib"]
    found = False
    for driver in drivers:
        # Make sure that SDL_VIDEODRIVER is set
        if "SDL_VIDEODRIVER" not in os.environ:
            os.environ["SDL_VIDEODRIVER"] = driver
        try:
            pygame.display.init()
        except pygame.error:
            del os.environ["SDL_VIDEODRIVER"]
            logger.warning("Driver: {0} failed.".format(driver))
            continue
        found = True
        break

    if not found:
        raise NoVideoDriverException("No suitable video driver found!")
    logger.info("Using SDL_VIDEODRIVER %s", os.environ["SDL_VIDEODRIVER"])

    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    logger.info("Framebuffer size: %d x %d" % (size[0], size[1]))
    flags = pygame.SCALED | pygame.FULLSCREEN | pygame.NOFRAME
    try:
        return pygame.display.set_mode((0, 0), flags)
    except Exception as e:
        raise NoVideoDriverException("Could not set video mode") from e
    # # Clear the screen to start
    # self.screen.fill((0, 0, 0))
    # # Initialise font support
    # pygame.font.init()
    # # Render the screen
    # pygame.display.update()
