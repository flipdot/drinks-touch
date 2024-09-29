from sqlalchemy.sql import text

from database.storage import get_session

_drink_cache = {}


def get_by_ean(ean):
    if ean in _drink_cache:
        return _drink_cache[ean]

    session = get_session()
    sql = text(
        """
        SELECT *
        FROM drink
        WHERE ean = :ean
    """
    )
    # stmt = select(Drink).where(Drink.ean == ean)

    row = session.connection().execute(sql, {"ean": ean}).fetchone()

    if row:
        drink = {
            "name": row.name,
            "size": row.size,
            "tags": ["unknown"],
            "ean": row.ean,
        }
        _drink_cache[ean] = drink
    else:
        drink = {
            "name": "Unbekannt (" + ean + ")",
            "size": 0,
            "tags": ["unknown"],
            "ean": ean,
        }

    return drink
