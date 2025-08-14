#!/usr/bin/env python3

from datetime import datetime
import json
import os
import re
import sys
import uuid

from PIL import Image, ImageDraw, ImageFont, ImageMath

from database.storage import Session, with_db
from env import is_pi
from sqlalchemy import text
from stats.flipdot import create_socket, send_frame, w, h

font = ImageFont.truetype(
    os.path.dirname(__file__) + "/../resources/fonts/slkscr.ttf", 7
)

max_drinks = 6

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

@with_db
def scans(limit=1000, hours=None):
    where = ""
    params = {}
    if hours:
        where = "WHERE tx.created_at > NOW() - INTERVAL ':hours HOUR'"
        params["hours"] = hours
    sql = text(
        """
    SELECT tx.id, tx.ean, tx.created_at, tx.account_id
    FROM tx
    LEFT OUTER JOIN drink d on tx.ean = d.ean
    %s
    ORDER BY created_at DESC
    LIMIT %d
    """
        % (where, int(limit))
    )
    sql_scans = Session().execute(sql, params).mappings().all()
    return [dict(row) for row in sql_scans]


def create_image(scan_list):
    image = Image.new("1", (w, h), 0)
    text_image = Image.new("1", (w, h), 0)
    draw = ImageDraw.Draw(image)
    text_draw = ImageDraw.Draw(text_image)

    drinks = {}
    max_count = 0
    for e in scan_list:
        name = e["name"]
        if not name:
            name = "Unknown"
            e["name"] = name
        if name not in drinks:
            drinks[name] = e
            drinks[name]["count"] = 1
        else:
            drinks[name]["count"] += 1
        if drinks[name]["count"] > max_count:
            max_count = drinks[name]["count"]

    drinks = list(drinks.values())
    drinks = sorted(drinks, key=lambda d: -d["count"])
    drinks = drinks[:max_drinks]
    if not drinks:
        return None
    width = w / len(drinks)
    for i, drink in enumerate(drinks):
        count = drink["count"]
        height = int(count * 1.0 / max_count * (h - 1))
        coords = [(width * i + 1, h - height), (int(width * (i + 1)) - 1, h)]
        draw.rectangle(coords, 1, 1)
        draw_drinkname(text_draw, width * i + 1, width, drink)
        _x = 0
        _y = 0
        for di in range(0, count):
            _x = di % (width - 5)
            _y = di / (width - 5)
            draw.point((width * i + _x * 2 + 2, h - 1 - _y * 2), 0)
    result = ImageMath.eval("255 - (a ^ b)", a=image, b=text_image)
    # result = ImageChops.add_modulo(image, text_image)
    # result = ImageChops.invert(result)
    return result


def draw_drinkname(text_draw, xoff, width, drink):
    name = drink["name"]
    split = re.split(r"[\- _,.]", name)
    x = 0
    y = 2
    for i, c in enumerate(split[0:3]):
        draw_char(text_draw, (xoff + x, -2 + y), c[0])
        x += 6
        if x + 6 > width:
            x = 0
            y += 6


char_offsets = {"C": (1, 0), "E": (1, 0), "G": (1, 0), "W": (1, 0), "F": (1, 0)}

special_chars = {"W": "#   #\n" + "#   #\n" + "# # #\n" + "# # #\n" + " # # \n"}


def draw_char(text_draw, pos, char):
    char = char.upper()
    if char in char_offsets:
        offx, offy = char_offsets[char]
        posx, posy = pos
        pos = (posx + offx, posy + offy)
    if char in special_chars:
        bitmap = special_chars[char]
        y = 2
        x = 0
        for p in bitmap:
            if p == "#":
                text_draw.point([x + pos[0], y + pos[1]], fill=1)
            x += 1
            if p == "\n":
                x = 0
                y += 1
    else:
        # pass
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


def main():
    run()


if __name__ == "__main__":
    main()
    sys.exit()
