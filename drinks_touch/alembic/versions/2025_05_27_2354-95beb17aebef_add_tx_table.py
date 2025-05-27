"""Add tx table

Revision ID: 95beb17aebef
Revises: 23c546d5907f
Create Date: 2025-05-27 23:54:43.442163

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "95beb17aebef"
down_revision: Union[str, None] = "23c546d5907f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tx",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("payment_reference", sa.Text(), nullable=True),
        sa.Column("ean", sa.Text(), nullable=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"], ["account.id"], name=op.f("fk_tx_account_id_account")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tx")),
    )
    op.drop_constraint("account_email_key", "account", type_="unique")
    op.drop_constraint("account_id_card_key", "account", type_="unique")
    op.drop_constraint("account_keycloak_sub_key", "account", type_="unique")
    op.drop_constraint("account_ldap_id_key", "account", type_="unique")
    op.drop_constraint("account_ldap_path_key", "account", type_="unique")
    op.drop_constraint("account_name_key", "account", type_="unique")
    op.drop_constraint("account_name_key1", "account", type_="unique")
    op.create_unique_constraint(op.f("uq_account_email"), "account", ["email"])
    op.create_unique_constraint(op.f("uq_account_id_card"), "account", ["id_card"])
    op.create_unique_constraint(
        op.f("uq_account_keycloak_sub"), "account", ["keycloak_sub"]
    )
    op.create_unique_constraint(op.f("uq_account_ldap_id"), "account", ["ldap_id"])
    op.create_unique_constraint(op.f("uq_account_ldap_path"), "account", ["ldap_path"])
    op.create_unique_constraint(op.f("uq_account_name"), "account", ["name"])
    op.add_column("rechargeevent", sa.Column("tx_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        op.f("fk_rechargeevent_tx_id_tx"), "rechargeevent", "tx", ["tx_id"], ["id"]
    )
    op.add_column("scanevent", sa.Column("tx_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        op.f("fk_scanevent_tx_id_tx"), "scanevent", "tx", ["tx_id"], ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("fk_scanevent_tx_id_tx"), "scanevent", type_="foreignkey")
    op.drop_column("scanevent", "tx_id")
    op.drop_constraint(
        op.f("fk_rechargeevent_tx_id_tx"), "rechargeevent", type_="foreignkey"
    )
    op.drop_column("rechargeevent", "tx_id")
    op.drop_constraint(op.f("uq_account_name"), "account", type_="unique")
    op.drop_constraint(op.f("uq_account_ldap_path"), "account", type_="unique")
    op.drop_constraint(op.f("uq_account_ldap_id"), "account", type_="unique")
    op.drop_constraint(op.f("uq_account_keycloak_sub"), "account", type_="unique")
    op.drop_constraint(op.f("uq_account_id_card"), "account", type_="unique")
    op.drop_constraint(op.f("uq_account_email"), "account", type_="unique")
    op.create_unique_constraint(
        "account_name_key1", "account", ["name"], postgresql_nulls_not_distinct=False
    )
    op.create_unique_constraint(
        "account_name_key", "account", ["name"], postgresql_nulls_not_distinct=False
    )
    op.create_unique_constraint(
        "account_ldap_path_key",
        "account",
        ["ldap_path"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        "account_ldap_id_key",
        "account",
        ["ldap_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        "account_keycloak_sub_key",
        "account",
        ["keycloak_sub"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        "account_id_card_key",
        "account",
        ["id_card"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        "account_email_key", "account", ["email"], postgresql_nulls_not_distinct=False
    )
    op.drop_table("tx")
