from sqlalchemy import select, delete

from database.models import Sale, Tx
from database.storage import with_db, Session
from tasks.base import BaseTask


class RebuildSalesTask(BaseTask):
    LABEL = "Rebuild Sales Statistics"

    @with_db
    def run(self):
        Session().execute(delete(Sale))

        query = select(Tx)
        txs = Session().execute(query).scalars().all()

        total_tx = len(txs)
        for i, tx in enumerate(txs):
            if self.sig_killed:
                break
            self.progress = (i + 1) / total_tx
            if tx.ean:
                sale = Sale(
                    ean=tx.ean,
                    date=tx.created_at,
                )
                Session().add(sale)
        Session().commit()
