"""init

Revision ID: 9acd27447795
Revises:
Create Date: 2025-03-09 21:16:03.848637

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9acd27447795"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "account",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ldap_id", sa.String(length=20), nullable=True),
        sa.Column("ldap_path", sa.String(length=50), nullable=True),
        sa.Column("keycloak_sub", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.Column("id_card", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("last_balance_warning_email_sent_at", sa.DateTime(), nullable=True),
        sa.Column("last_summary_email_sent_at", sa.DateTime(), nullable=True),
        sa.Column(
            "summary_email_notification_setting", sa.String(length=50), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("id_card"),
        sa.UniqueConstraint("keycloak_sub"),
        sa.UniqueConstraint("ldap_id"),
        sa.UniqueConstraint("ldap_path"),
    )
    op.create_table(
        "drink",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ean", sa.String(length=20), nullable=True),
        sa.Column("name", sa.String(length=40), nullable=True),
        sa.Column("size", sa.Numeric(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rechargeevent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=20), nullable=True),
        sa.Column("helper_user_id", sa.String(length=20), nullable=True),
        sa.Column("amount", sa.Numeric(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "scanevent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("barcode", sa.String(length=20), nullable=True),
        sa.Column("user_id", sa.String(length=20), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("uploaded_to_influx", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tetris__game",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("highscore", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("lines", sa.Integer(), nullable=False),
        sa.Column("next_blocks", sa.JSON(), nullable=True),
        sa.Column("board", sa.JSON(), nullable=True),
        sa.Column("reserve_block", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tetris__players",
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("blocks", sa.Integer(), nullable=False),
        sa.Column("lines", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("alltime_score", sa.Integer(), nullable=False),
        sa.Column("alltime_blocks", sa.Integer(), nullable=False),
        sa.Column("alltime_lines", sa.Integer(), nullable=False),
        sa.Column("alltime_points", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["account.id"],
        ),
        sa.PrimaryKeyConstraint("account_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tetris__players")
    op.drop_table("tetris__game")
    op.drop_table("scanevent")
    op.drop_table("rechargeevent")
    op.drop_table("drink")
    op.drop_table("account")
