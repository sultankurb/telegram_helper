"""admin table

Revision ID: 7e1ced59ef63
Revises:
Create Date: 2026-05-29 17:39:16.423200

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7e1ced59ef63"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("telegram_pk", sa.BigInteger(), nullable=False),
        sa.Column("pk", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("telegram_pk"),
    )


def downgrade() -> None:
    op.drop_table("admins")
