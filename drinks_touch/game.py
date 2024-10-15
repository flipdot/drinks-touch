#!/usr/bin/env python3

import contextlib
import locale
import logging
import os
import queue
import subprocess
import sys
import threading
import time

import config
import env
from database.storage import init_db, Session
from drinks.drinks_manager import DrinksManager
from notifications.notification import send_low_balances, send_summaries
from screen import get_screen
from screens.screen_manager import ScreenManager
from screens.sync import SyncScreen
from stats.stats import run as stats_send
from users.sync import sync_recharges
from webserver.webserver import run as run_webserver
import sentry_sdk
from ldap3.utils.log import (
    set_library_log_detail_level,
    set_library_log_activation_level,
    EXTENDED,
)

with contextlib.redirect_stdout(None):
    import pygame

sentry_sdk.init(config.SENTRY_DSN)

logging.basicConfig(
    level=getattr(logging, config.LOGLEVEL),
    format="[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s",
)
logging.Formatter.converter = time.gmtime

# ldap log level
set_library_log_activation_level(logging.CRITICAL)
if config.LOGLEVEL == logging.DEBUG:
    set_library_log_detail_level(EXTENDED)

event_queue = queue.Queue()
screen_manager = None


def handle_events():
    while True:
        events = []
        while True:
            block = len(events) == 0
            try:
                events.append(event_queue.get(block))
            except queue.Empty:
                break
        current_screen = screen_manager.get_active()
        try:
            current_screen.events(events)
        except Exception:
            logging.exception("handling events:")


def stats_loop():
    i = 0
    while True:
        # stats_send()
        with Session.begin():
            send_low_balances()
            if env.is_pi():
                sync_recharges()
            if i % 60 * 12 == 0:
                send_summaries()
        time.sleep(60)
        i += 1
        i %= 60 * 12


# Rendering #
def main(argv):
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

    if "--webserver" in argv:
        run_webserver()
        return 0

    if "--stats" in argv:
        stats_send()
        return 0

    screen = get_screen()
    clock = pygame.time.Clock()

    drinks_manager = DrinksManager()
    DrinksManager.set_instance(drinks_manager)

    global screen_manager
    screen_manager = ScreenManager(screen)
    screen_manager.set_active(SyncScreen(screen))
    ScreenManager.set_instance(screen_manager)

    init_db()

    # webserver needs to be a main thread #
    web_thread = subprocess.Popen([sys.argv[0], "--webserver"])

    event_thread = threading.Thread(target=handle_events)
    event_thread.daemon = True
    event_thread.start()

    stats_thread = threading.Thread(target=stats_loop)
    stats_thread.daemon = True
    # TODO: This is causing transaction errors
    # stats_thread.start()

    if env.is_pi():
        os.system("rsync -a sounds/ pi@pixelfun:sounds/ &")

    t = 0
    done = False

    while not done:
        dt = clock.tick(config.FPS) / 1000.0
        t += dt

        current_screen = screen_manager.get_active()

        screen.fill((0, 0, 0))
        current_screen.render(dt)

        pygame.display.flip()

        events = pygame.event.get()
        for e in events:
            e.t = t
            e.dt = dt
            if e.type == pygame.QUIT or (
                e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE
            ):
                done = True
                break
            event_queue.put(e, True)

    web_thread.terminate()
    web_thread.wait()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
