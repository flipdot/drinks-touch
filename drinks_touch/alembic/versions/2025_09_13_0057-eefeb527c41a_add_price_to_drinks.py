"""Add price to drinks

Revision ID: eefeb527c41a
Revises: ec6ef260acfd
Create Date: 2025-09-13 00:57:44.442426

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "eefeb527c41a"
down_revision: Union[str, None] = "ec6ef260acfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "drink", sa.Column("price", sa.Numeric(precision=8, scale=2), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("drink", "price")
