"""Add tx_history_visible column

Revision ID: 41afc5afd75b
Revises: 858dadbc3869
Create Date: 2025-08-01 21:19:25.676367

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "41afc5afd75b"
down_revision: Union[str, None] = "858dadbc3869"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "account", sa.Column("tx_history_visible", sa.Boolean(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("account", "tx_history_visible")
