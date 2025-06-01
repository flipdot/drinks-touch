from sqlalchemy import select

from database.models import Drink
from database.storage import Session

_drink_cache = {}


def get_by_ean(ean):
    if ean in _drink_cache:
        return _drink_cache[ean]

    query = select(Drink).where(Drink.ean == ean)

    with Session() as session:
        drink = session.scalars(query).one_or_none()

    if drink:
        legacy_drink = {
            "name": drink.name,
            "size": drink.size,
            "tags": ["unknown"],
            "ean": drink.ean,
        }
        _drink_cache[ean] = legacy_drink
    else:
        legacy_drink = {
            "name": "Unbekannt",
            "size": 0,
            "tags": ["unknown"],
            "ean": ean,
        }

    return legacy_drink
