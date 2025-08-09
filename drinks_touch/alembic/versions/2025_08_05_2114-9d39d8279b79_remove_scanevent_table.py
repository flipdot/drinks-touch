"""Remove ScanEvent table

Revision ID: 9d39d8279b79
Revises: 41afc5afd75b
Create Date: 2025-08-05 21:14:51.872736

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9d39d8279b79"
down_revision: Union[str, None] = "41afc5afd75b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("scanevent")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "scanevent",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("barcode", sa.VARCHAR(length=20), autoincrement=False, nullable=True),
        sa.Column("user_id", sa.VARCHAR(length=20), autoincrement=False, nullable=True),
        sa.Column(
            "timestamp", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "uploaded_to_influx", sa.BOOLEAN(), autoincrement=False, nullable=True
        ),
        sa.Column("tx_id", sa.UUID(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["tx_id"], ["tx.id"], name=op.f("fk_scanevent_tx_id_tx")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("scanevent_pkey")),
    )
