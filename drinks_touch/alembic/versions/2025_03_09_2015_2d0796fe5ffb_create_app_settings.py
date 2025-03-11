"""Create app settings and unique account names

Revision ID: 2d0796fe5ffb
Revises: 9acd27447795
Create Date: 2025-03-09 21:19:28.712504

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2d0796fe5ffb"
down_revision: Union[str, None] = "9acd27447795"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "appsettings",
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("value", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_unique_constraint(None, "account", ["name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "account", type_="unique")
    op.drop_table("appsettings")
