from database.models import ScanEvent, Tx, Drink, Account, RechargeEvent
from database.storage import Session, with_db
from tasks.base import BaseTask


class MigrateTxTask(BaseTask):
    LABEL = "Migriere Scan- und Rechargeevents zu Transaktionen"

    def run(self):
        self._migrate_scanevents()
        self._migrate_rechargeevents()
        self._check_dangling_txs()

    @with_db
    def _migrate_scanevents(self):
        self.logger.info("Selecting non-migrated scanevents")

        scanevents_with_accounts = (
            Session()
            .query(ScanEvent, Account)
            .join(Account, ScanEvent.user_id == Account.ldap_id)
            .filter(
                ScanEvent.tx_id.is_(None),
                ScanEvent.user_id != "0",
                ~ScanEvent.user_id.startswith("geld-"),
            )
            .all()
        )

        total_events = len(scanevents_with_accounts)
        self.logger.info("Found {} scanevents".format(total_events))
        for i, (scanevent, account) in enumerate(scanevents_with_accounts):
            if self.sig_killed:
                break
            self.progress = (i + 1) / total_events

            drink = Drink.query.filter(
                Drink.ean == scanevent.barcode,
            ).one_or_none()

            name = drink.name if drink else "Unbekannt"
            self.logger.info(f"{account.name:15}: {name} ({scanevent.barcode})")

            tx = Tx(
                created_at=scanevent.timestamp,
                payment_reference=f'Kauf "{name}"',
                ean=scanevent.barcode,
                amount=-1,
                account_id=account.id,
            )
            Session().add(tx)
            Session().flush()
            scanevent.tx_id = tx.id

    @with_db
    def _migrate_rechargeevents(self):
        self.logger.info("Selecting non-migrated rechargeevents")
        rechargevents_with_accounts = (
            Session()
            .query(RechargeEvent, Account)
            .join(Account, RechargeEvent.user_id == Account.ldap_id)
            .filter(
                RechargeEvent.tx_id.is_(None),
                ~RechargeEvent.user_id.startswith("geld-"),
            )
            .all()
        )
        total_events = len(rechargevents_with_accounts)
        self.logger.info("Found {} rechargeevents".format(total_events))
        for i, (rechargeevent, account) in enumerate(rechargevents_with_accounts):
            if self.sig_killed:
                break
            self.progress = (i + 1) / total_events

            if not rechargeevent.user_id:
                self.logger.warning(
                    f"RechargeEvent #{rechargeevent.id} has no user_id, skipping"
                )
                continue

            if rechargeevent.helper_user_id == "DISPLAY":
                payment_reference = "Aufladung via Display"
            else:
                # Try to find a recharge event on the same day for the helper user
                # with the same amount, but negative. In this case, it's a transfer
                # to the helper user.
                is_transfer = (
                    Session()
                    .query(
                        RechargeEvent.query.filter(
                            RechargeEvent.helper_user_id == account.name,
                            RechargeEvent.amount == -rechargeevent.amount,
                            RechargeEvent.timestamp
                            >= rechargeevent.timestamp.replace(
                                hour=0, minute=0, second=0, microsecond=0
                            ),
                            RechargeEvent.timestamp
                            < rechargeevent.timestamp.replace(
                                hour=23, minute=59, second=59, microsecond=999999
                            ),
                        ).exists()
                    )
                    .scalar()
                )

                if is_transfer and rechargeevent.amount > 0:
                    payment_reference = f"Übertrag von {rechargeevent.helper_user_id}"
                elif is_transfer and rechargeevent.amount < 0:
                    payment_reference = f"Übertrag an {rechargeevent.helper_user_id}"
                else:
                    payment_reference = "Aufladung via Web"

            tx = Tx(
                created_at=rechargeevent.timestamp,
                payment_reference=payment_reference,
                amount=rechargeevent.amount,
                account_id=account.id,
            )
            Session().add(tx)
            Session().flush()
            rechargeevent.tx_id = tx.id

    @with_db
    def _check_dangling_txs(self):
        """
        Find transactions that are not linked to any scan or recharge event.
        """
        self.logger.info("Checking for dangling transactions")
        txs = (
            Session()
            .query(Tx)
            .outerjoin(RechargeEvent, Tx.id == RechargeEvent.tx_id)
            .outerjoin(ScanEvent, Tx.id == ScanEvent.tx_id)
            .filter(RechargeEvent.tx_id.is_(None), ScanEvent.tx_id.is_(None))
            .all()
        )
        self.logger.info("Found {} dangling transactions".format(len(txs)))
        for tx in txs:
            self.logger.warning(f'Deleting "{tx.payment_reference}" ({tx.id})')
            Session().delete(tx)
        self.logger.info("Deleted dangling transactions")
