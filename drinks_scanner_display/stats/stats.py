#!/usr/bin/env python2

import sys
import re
import time

from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageMath

from env import is_pi
from flipdot import create_socket, send_frame, w, h

from database.storage import get_session
from database.storage import init_db

font = ImageFont.truetype("drinks_scanner_display/resources/fonts/slkscr.ttf", 7)

max_drinks = 6

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
    LEFT OUTER JOIN drink d on se.barcode = d.ean
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
        if not name:
            name = 'Unknown'
            e['name'] = name
        if name not in drinks:
            drinks[name] = e
            drinks[name]['count'] = 1
        else:
            drinks[name]['count'] += 1
        if drinks[name]['count'] > max_count:
            max_count = drinks[name]['count']
        
    drinks = list(drinks.values())
    drinks = sorted(drinks, key=lambda d:-d['count'])
    drinks = drinks[:max_drinks]
    if not drinks:
        return None
    width = w / len(drinks)
    for i, drink in enumerate(drinks):
        count = drink['count']
        height = int(count * 1.0 / max_count * (h-1))
        coords = [(width * i + 1, h), (int(width*(i+1)) - 1, h-height)]
        draw.rectangle(coords, 1, 1)
        draw_drinkname(text_draw, width*i+1, width, drink)
        _x = 0
        _y = 0
        for di in range(0,count):
            _x = di % (width - 5)
            _y = di / (width - 5)
            draw.point((
                width * i + _x * 2 + 2,
                h - 1 - _y*2
                ), 0)
    result = ImageMath.eval("255 - (a ^ b)", a=image, b=text_image)
    #result = ImageChops.add_modulo(image, text_image)
    #result = ImageChops.invert(result)
    return result

def draw_drinkname(text_draw, xoff, width, drink):
    name = drink['name']
    split = re.split(r"[\- _,\.]", name)
    x = 0
    y = 2
    for i, c in enumerate(split[0:3]):
        draw_char(text_draw, (xoff + x, -2 + y), c[0])
        x += 6
        if x + 6 > width:
            x = 0
            y += 6

char_offsets = {
    'C': (1, 0), 'E': (1, 0), 'G': (1,0),
    'W': (1,0), 'F': (1,0)
}
special_chars = {
    'W': "#   #\n" + 
         "#   #\n" +
         "# # #\n" +
         "# # #\n" +
         " # # \n"
}
def draw_char(text_draw, pos, char):
    char = char.upper()
    if char in char_offsets:
        offx, offy = char_offsets[char]
        posx, posy = pos
        pos = (posx + offx, posy + offy)
    if char in special_chars:
        bitmap = special_chars[char]
        y=2
        x=0
        for p in bitmap:
            if p == '#':
                text_draw.point([x+pos[0], y+pos[1]], fill=1)
            x += 1
            if p == '\n':
                x = 0
                y += 1
    else:
        #pass
        text_draw.text(pos, char, 1, font=font)

def run():
    if not is_pi():
        return
    scan_list = scans(limit=1000, hours=24)
    image = create_image(scan_list)
    if not image:
        return
    socket = create_socket()
    send_frame(socket, image)

def main(argv):
    run()

if __name__ == "__main__":
    sys.exit(main(sys.argv))