#!/usr/bin/env python2
# coding=utf-8
import pygame
import logging
import threading
import subprocess
import Queue
import traceback
import sys
import os
import time

logging.basicConfig(level=logging.DEBUG)

from database.storage import init_db

from pygame.locals import *
from screen import get_screen
from screens.screen_manager import ScreenManager
from drinks.drinks_manager import DrinksManager

from webserver.webserver import run as run_webserver
from stats.stats import run as stats_send
from notifications.notification import send_lowbalances, send_summaries
from barcode.barcode_reader import run as run_barcode_reader
from barcode.barcode_worker import Worker as BarcodeWorker

import debug
debug.listen()

event_queue = Queue.Queue()
screen_manager = None

#### Events ####
def handle_events():
    while True:
        events = []
        while True:
            block = len(events) == 0
            try:
                events.append(event_queue.get(block))
            except Queue.Empty:
                break
        current_screen = screen_manager.get_active()
        try:
            current_screen.events(events)
        except Exception as e:
            print e
            pass

def stats_loop():
    while True:
        stats_send()
        send_lowbalances()
        send_summaries()
        time.sleep(60)

##### Rendering #####
def main(argv):

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
    ScreenManager.set_instance(screen_manager)

    init_db()

    ##### Barcode Scanner #####
    barcode_worker = BarcodeWorker()
    barcode_thread = threading.Thread(
        target=run_barcode_reader,
        args=(barcode_worker,)
    )
    barcode_thread.daemon = True
    barcode_thread.start()

    ##### webserver needs to be a main thread #####
    web_thread = subprocess.Popen([sys.argv[0], "--webserver"])

    event_thread = threading.Thread(
        target=handle_events
    )
    event_thread.daemon = True
    event_thread.start()

    stats_thread = threading.Thread(
        target=stats_loop
    )
    stats_thread.daemon = True
    stats_thread.start()

    os.system("rsync -a sounds/ pi@pixelfun:sounds/ &")

    t = 0
    dt = 0
    done = False
    while not done:
        dt = clock.tick(30) / 1000.0
        t += dt

        current_screen = screen_manager.get_active()

        screen.fill((0, 0, 0))
        current_screen.render(t, dt)

        pygame.display.flip()

        events = pygame.event.get()
        for e in events:
            e.t = t
            e.dt = dt
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                done = True
                break
            event_queue.put(e, True)
    web_thread.terminate()
    web_thread.wait()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))