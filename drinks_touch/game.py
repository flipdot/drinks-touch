#!/usr/bin/env python3

import contextlib
import locale
import logging
import os
import queue
import subprocess
import sys
import time
from pathlib import Path

from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

import config
import env
from database.storage import engine
from drinks.drinks_manager import DrinksManager
from overlays import MouseOverlay, BaseOverlay
from overlays.keyboard import KeyboardOverlay
from screens.message_screen import MessageScreen
from screens.screen_manager import ScreenManager

from screens.tasks_screen import TasksScreen
from stats.stats import run as stats_send
from webserver.webserver import run as run_webserver
import sentry_sdk

with contextlib.redirect_stdout(None):
    import pygame

sentry_sdk.init(config.SENTRY_DSN)

logging.basicConfig(
    level=getattr(logging, config.LOGLEVEL),
    format="[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(name)s: %(message)s",
)
logging.Formatter.converter = time.gmtime
# Uncomment to see which SQL queries are executed
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

event_queue = queue.Queue()
overlays: list[BaseOverlay] = []
screen_manager: ScreenManager | None = None


def handle_events(events, t: int, dt: float) -> bool:
    for e in events:
        e.t = t
        e.dt = dt
        if e.type == pygame.QUIT:
            return True
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            if screen_manager.active_object is None:
                return True
            else:
                screen_manager.active_object = None
    for overlay in overlays[::-1]:
        overlay.events(events)
    screen_manager.events(events)
    return False


# Rendering #
def main(argv):
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

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

    alembic_script = ScriptDirectory(Path(__file__).parent / "alembic")
    with engine.begin() as conn:
        context = MigrationContext.configure(conn)
        if context.get_current_revision() != alembic_script.get_current_head():
            screen_manager.set_active(
                MessageScreen(
                    title="Database error",
                    message=[
                        "The database isn't up to date. Please run:",
                        "",
                        "$ alembic upgrade head",
                        "",
                        f"Current revision: {context.get_current_revision()}",
                        f"Head revision:    {alembic_script.get_current_head()}",
                        "",
                        "If you continue, the application might not work",
                        "as expected.",
                    ],
                ),
                replace=True,
            )
        else:
            screen_manager.set_active(TasksScreen())

    overlays.extend(
        [
            KeyboardOverlay(screen_manager),
            MouseOverlay(screen_manager),
        ]
    )

    # webserver needs to be a main thread #
    web_process = subprocess.Popen([sys.argv[0], "--webserver"])

    if env.is_pi():
        os.system("rsync -a sounds/ pi@pixelfun:sounds/ &")

    pygame.key.set_repeat(500, 50)
    pygame.mixer.pre_init(48000, buffer=2048)
    pygame.mixer.init()

    t = 0
    done = False

    while not done:
        dt = clock.tick(config.FPS) / 1000.0
        t += dt

        done = handle_events(pygame.event.get(), t, dt)

        screen_manager.render(dt)
        for overlay in overlays:
            overlay.render(dt)

        pygame.display.flip()

    web_process.terminate()
    web_process.wait()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
