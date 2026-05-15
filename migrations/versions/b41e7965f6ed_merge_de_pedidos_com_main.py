"""merge de pedidos com main

Revision ID: b41e7965f6ed
Revises: 1f32fc4f41bc, 7db2835f4a6f
Create Date: 2026-05-15 14:23:09.274547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b41e7965f6ed'
down_revision = ('1f32fc4f41bc', '7db2835f4a6f')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass