from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from database.storage import with_db_session

_drink_cache = {}


@with_db_session
def get_by_ean(ean, session: Session):
    if ean in _drink_cache:
        return _drink_cache[ean]

    sql = text(
        """
        SELECT *
        FROM drink
        WHERE ean = :ean
    """
    )
    # stmt = select(Drink).where(Drink.ean == ean)

    row = session.execute(sql, {"ean": ean}).fetchone()

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
            "name": "Unbekannt",
            "size": 0,
            "tags": ["unknown"],
            "ean": ean,
        }

    return drink
