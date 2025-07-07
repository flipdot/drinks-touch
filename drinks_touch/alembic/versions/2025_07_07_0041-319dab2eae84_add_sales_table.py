"""Add sales table

Revision ID: 319dab2eae84
Revises: 95beb17aebef
Create Date: 2025-07-07 00:41:31.321624

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "319dab2eae84"
down_revision: Union[str, None] = "95beb17aebef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sales",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "date",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=False,
        ),
        sa.Column("ean", sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sales")
