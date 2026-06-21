"""Replace keycloak with local jwt auth

Revision ID: a1b2c3d4e5f6
Revises: c3d4e5f6a7b8, fda084f220cd
Create Date: 2026-06-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = ('c3d4e5f6a7b8', 'fda084f220cd')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename senha to senha_hash first
    op.alter_column('usuarios', 'senha', new_column_name='senha_hash', existing_type=sa.String(255))

    # Set a default hash for any null values (hashed "changeme")
    op.execute("""
        UPDATE usuarios
        SET senha_hash = '$2b$12$VIQjxLe2RZ1KFjXS6U4aYu3iBtfZlPj4Z5e3Pq9qKJ5p8mK3pHK1m'
        WHERE senha_hash IS NULL
    """)

    # Now make senha_hash non-nullable
    op.alter_column('usuarios', 'senha_hash', nullable=False, existing_type=sa.String(255))

    # Drop keycloak_id column
    op.drop_column('usuarios', 'keycloak_id')


def downgrade() -> None:
    # Reverse: make senha_hash nullable again
    op.alter_column('usuarios', 'senha_hash', nullable=True, existing_type=sa.String(255))

    # Rename back
    op.alter_column('usuarios', 'senha_hash', new_column_name='senha')

    # Add keycloak_id back
    op.add_column('usuarios', sa.Column('keycloak_id', sa.String(64), nullable=True, unique=True, index=True))
