"""Add 'last_sepa_deposit' date column

Revision ID: ec6ef260acfd
Revises: 9d39d8279b79
Create Date: 2025-08-19 20:45:07.294223

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ec6ef260acfd"
down_revision: Union[str, None] = "9d39d8279b79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("account", sa.Column("last_sepa_deposit", sa.Date(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("account", "last_sepa_deposit")
