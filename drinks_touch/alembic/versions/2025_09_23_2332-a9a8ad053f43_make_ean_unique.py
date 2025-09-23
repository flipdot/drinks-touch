"""Make ean unique

Revision ID: a9a8ad053f43
Revises: eefeb527c41a
Create Date: 2025-09-23 23:32:11.788306

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a9a8ad053f43"
down_revision: Union[str, None] = "eefeb527c41a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(op.f("uq_drink_ean"), "drink", ["ean"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_drink_ean"), "drink", type_="unique")
