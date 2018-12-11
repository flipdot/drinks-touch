import logging
import os

import contextlib
with contextlib.redirect_stdout(None):
    import pygame

logger = logging.getLogger(__name__)


def get_screen():
    try:
        screen = __get_screen_framebuffer()
    except Exception:
        screen = __get_screen_xserver()

    return screen


def __get_screen_xserver():
    SIZE = 480, 800
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    return screen


def __get_screen_framebuffer():
    # Ininitializes a new pygame screen using the framebuffer
    # Based on "Python GUI in Linux frame buffer"
    # http://www.karoltomala.com/blog/?p=679
    disp_no = os.getenv("DISPLAY")
    if disp_no:
        logger.info("I'm running under X display = {0}".format(disp_no))

    # Check which frame buffer drivers are available
    # Start with fbcon since directfb hangs with composite output
    drivers = ['fbcon', 'directfb', 'svgalib']
    found = False
    for driver in drivers:
        # Make sure that SDL_VIDEODRIVER is set
        if 'SDL_VIDEODRIVER' not in os.environ:
            os.environ['SDL_VIDEODRIVER'] = driver
        try:
            pygame.display.init()
        except pygame.error:
            del os.environ['SDL_VIDEODRIVER']
            logger.warning('Driver: {0} failed.'.format(driver))
            continue
        found = True
        break

    if not found:
        raise Exception('No suitable video driver found!')

    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    print("Framebuffer size: %d x %d" % (size[0], size[1]))
    return pygame.display.set_mode(size, pygame.FULLSCREEN)
    # # Clear the screen to start
    # self.screen.fill((0, 0, 0))
    # # Initialise font support
    # pygame.font.init()
    # # Render the screen
    # pygame.display.update()
