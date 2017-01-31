# coding=utf-8

from database.storage import get_session
from sqlalchemy.sql import text

_drink_cache = {}

def get_by_ean(ean):
    if ean in _drink_cache:
        return _drink_cache[ean]
    session = get_session()
    sql = text("""
        SELECT *
        FROM drink
        WHERE ean = :ean
    """)
    row = session.connection().execute(sql, ean=ean).fetchone()
    if row:
        drink = dict(zip(row.keys(), row))
        _drink_cache[ean] = drink
    else: 
        drink = {
            'name': 'Unbekannt ('+ean+')',
            'size': 0,
            'tags': ['unknown'],
            'ean': ean
        }

    return drink