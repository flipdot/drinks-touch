"""Add account enabled column

Revision ID: 23c546d5907f
Revises: 2d0796fe5ffb
Create Date: 2025-03-09 23:04:06.654036

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "23c546d5907f"
down_revision: Union[str, None] = "2d0796fe5ffb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("account", sa.Column("enabled", sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("account", "enabled")
