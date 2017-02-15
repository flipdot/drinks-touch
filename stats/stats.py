#!/usr/bin/env python2

import sys
import re
import time

from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageMath

from flipdot import create_socket, send_frame, w, h

from database.storage import get_session
from database.storage import init_db

font = ImageFont.truetype("stats/slkscr.ttf", 7)

def scans(limit=1000, hours=None):
    session = get_session()
    where = ""
    params = {}
    if hours:
        where = "WHERE se.timestamp > NOW() - INTERVAL ':hours HOUR'"
        params['hours'] = hours
    sql = """
    SELECT se.id, barcode, se.timestamp, name
    FROM scanevent se
    JOIN drink d on se.barcode = d.ean
    %s
    ORDER BY timestamp DESC
    LIMIT %d
    """ % (where, limit)
    scans = session.execute(sql, params).fetchall()
    return [dict(zip(row.keys(), row)) for row in scans]

def create_image(scan_list):
    image = Image.new("1", (w, h), 0)
    text_image = Image.new("1", (w, h), 0)
    draw = ImageDraw.Draw(image)
    text_draw = ImageDraw.Draw(text_image)

    drinks = {}
    max_count = 0
    for e in scan_list:
        name = e['name']
        if name not in drinks:
            drinks[name] = e
            drinks[name]['count'] = 1
        else:
            drinks[name]['count'] += 1
        if drinks[name]['count'] > max_count:
            max_count = drinks[name]['count']

    drinks = list(drinks.values())
    drinks = sorted(drinks, key=lambda d:-d['count'])
    drinks = drinks[0:8]
    if not drinks:
        return None
    width = w / len(drinks)
    for i, drink in enumerate(drinks):
        height = int(drink['count'] * 1.0 / max_count * h)
        coords = [(width * i, h), (int(width*(i+0.8)), h-height)]
        #print drink['name'], drink['count'], coords
        draw.rectangle(coords, 1, 1)
        draw_drinkname(text_draw, width*i, drink)
    result = ImageMath.eval("255 - (a ^ b)", a=image, b=text_image)
    #result = ImageChops.add_modulo(image, text_image)
    #result = ImageChops.invert(result)
    return result

def draw_drinkname(text_draw, xoff, drink):
    name = drink['name']
    split = re.split(r"[\- _,\.]", name)
    for i, c in enumerate(split[0:2]):
        draw_char(text_draw, (xoff, -2 + 6*i), c[0])

char_offsets = {'M': (-1, 0), 'C': (-1, 0)}
def draw_char(text_draw, pos, char):
    if char in char_offsets:
        offx, offy = char_offsets[char]
        posx, posy = pos
        pos = (posx + offx, posy + offy)
    text_draw.text(pos, char, 1, font=font)

def run():
    scan_list = scans(limit=1000, hours=48)
    image = create_image(scan_list)
    if not image:
        return
    socket = create_socket()
    send_frame(socket, image)

def run_loop():
    while True:
        run()
        time.sleep(60)

def main(argv):
    run()

if __name__ == "__main__":
    sys.exit(main(sys.argv))