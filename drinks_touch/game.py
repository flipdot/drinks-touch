#!/usr/bin/env python3

import contextlib
import locale
import logging
import os
import queue
import random
import subprocess
import sys
import threading
import time

import config
import env
from database.models import Account
from database.storage import init_db, Session
from drinks.drinks_manager import DrinksManager
from notifications.notification import send_low_balances, send_summaries
from overlays import MouseOverlay, BaseOverlay
from overlays.keyboard import KeyboardOverlay
from screens.screen_manager import ScreenManager

# from screens.tasks_screen import TasksScreen
from screens.tetris import TetrisScreen
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
    format="[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(name)s: %(message)s",
)
logging.Formatter.converter = time.gmtime

# ldap log level
set_library_log_activation_level(logging.CRITICAL)
if config.LOGLEVEL == logging.DEBUG:
    set_library_log_detail_level(EXTENDED)

event_queue = queue.Queue()
overlays: list[BaseOverlay] = []
screen_manager: ScreenManager | None = None


def handle_events():
    while True:
        events = []
        while True:
            block = len(events) == 0
            try:
                events.append(event_queue.get(block))
            except queue.Empty:
                break
        for overlay in overlays[::-1]:
            overlay.events(events)

        screen_manager.events(events)


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

    init_db()

    if "--webserver" in argv:
        run_webserver()
        return 0

    if "--stats" in argv:
        stats_send()
        return 0

    clock = pygame.time.Clock()

    DrinksManager()

    global screen_manager
    global overlays
    screen_manager = ScreenManager()

    screen_manager.set_default()
    # screen_manager.set_active(TasksScreen())
    screen_manager.set_active(TetrisScreen(Account.query.all()[random.randint(0, 5)]))

    overlays.extend(
        [
            KeyboardOverlay(screen_manager),
            MouseOverlay(screen_manager),
        ]
    )

    # webserver needs to be a main thread #
    web_thread = subprocess.Popen([sys.argv[0], "--webserver"])

    event_thread = threading.Thread(target=handle_events)
    event_thread.daemon = True
    event_thread.start()

    stats_thread = threading.Thread(target=stats_loop)
    stats_thread.daemon = True
    stats_thread.start()

    if env.is_pi():
        os.system("rsync -a sounds/ pi@pixelfun:sounds/ &")

    pygame.key.set_repeat(500, 50)
    pygame.mixer.init()

    t = 0
    done = False

    while not done:
        dt = clock.tick(config.FPS) / 1000.0
        t += dt

        screen_manager.render(dt)
        for overlay in overlays:
            overlay.render(dt)

        pygame.display.flip()

        events = pygame.event.get()
        for e in events:
            e.t = t
            e.dt = dt
            if e.type == pygame.QUIT:
                done = True
                break
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                if screen_manager.active_object is None:
                    done = True
                    break
                else:
                    screen_manager.active_object = None
            event_queue.put(e, True)

    web_thread.terminate()
    web_thread.wait()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
