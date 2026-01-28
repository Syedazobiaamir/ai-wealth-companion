"""Initial schema with all Phase II tables.

Revision ID: 001
Revises:
Create Date: 2026-01-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create category table
    op.create_table(
        "category",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("emoji", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_category_name"), "category", ["name"], unique=True)

    # Create user table
    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("theme", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create transaction table
    op.create_table(
        "transaction",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("note", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("recurring", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transaction_date"), "transaction", ["date"], unique=False)
    op.create_index(op.f("ix_transaction_category_id"), "transaction", ["category_id"], unique=False)
    op.create_index(op.f("ix_transaction_type"), "transaction", ["type"], unique=False)
    op.create_index(op.f("ix_transaction_deleted_at"), "transaction", ["deleted_at"], unique=False)

    # Create budget table
    op.create_table(
        "budget",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("limit_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category_id", "month", "year", name="uq_budget_category_month_year"),
    )


def downgrade() -> None:
    op.drop_table("budget")
    op.drop_index(op.f("ix_transaction_deleted_at"), table_name="transaction")
    op.drop_index(op.f("ix_transaction_type"), table_name="transaction")
    op.drop_index(op.f("ix_transaction_category_id"), table_name="transaction")
    op.drop_index(op.f("ix_transaction_date"), table_name="transaction")
    op.drop_table("transaction")
    op.drop_table("user")
    op.drop_index(op.f("ix_category_name"), table_name="category")
    op.drop_table("category")
