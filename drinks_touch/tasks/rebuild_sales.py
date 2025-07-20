from sqlalchemy import select, delete

from database.models import Sale, Tx
from database.storage import with_db, Session
from tasks.base import BaseTask


class RebuildSalesTask(BaseTask):
    LABEL = "Rebuild Sales Statistics"

    @with_db
    def run(self):
        res = Session().execute(delete(Sale))

        self.logger.info(f"Deleted {res.rowcount} sales records")

        query = select(Tx)
        txs = Session().execute(query).scalars().all()

        total_tx = len(txs)

        self.logger.info(f"Found {total_tx} transactions.")
        self.logger.info("Creating a record for each sale…")
        sales = 0
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
                sales += 1
        self.logger.info(f"Created {sales} sales records.")
        self.logger.info("Committing changes to the database")
        Session().commit()
