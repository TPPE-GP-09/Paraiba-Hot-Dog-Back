"""update user role enum to numeric values

Revision ID: 0002_update_user_role_enum
Revises: 0001_create_users_table
Create Date: 2026-04-27
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_update_user_role_enum"
down_revision = "0001_create_users_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            has_admin boolean;
            has_zero boolean;
        BEGIN
            SELECT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'user_role' AND e.enumlabel = 'admin'
            ) INTO has_admin;

            SELECT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'user_role' AND e.enumlabel = '0'
            ) INTO has_zero;

            IF has_admin AND NOT has_zero THEN
                CREATE TYPE user_role_new AS ENUM ('0', '1', '2');

                ALTER TABLE users
                    ALTER COLUMN role TYPE user_role_new
                    USING CASE role
                        WHEN 'admin' THEN '0'
                        WHEN 'caixa' THEN '1'
                        WHEN 'cozinha' THEN '2'
                        ELSE role::text
                    END::user_role_new;

                DROP TYPE user_role;
                ALTER TYPE user_role_new RENAME TO user_role;
            ELSIF has_zero THEN
                NULL;
            ELSE
                BEGIN
                    CREATE TYPE user_role AS ENUM ('0', '1', '2');
                EXCEPTION
                    WHEN duplicate_object THEN NULL;
                END;
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            has_text boolean;
            has_zero boolean;
        BEGIN
            SELECT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'user_role' AND e.enumlabel = 'admin'
            ) INTO has_text;

            SELECT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'user_role' AND e.enumlabel = '0'
            ) INTO has_zero;

            IF has_zero AND NOT has_text THEN
                CREATE TYPE user_role_old AS ENUM ('admin', 'caixa', 'cozinha');

                ALTER TABLE users
                    ALTER COLUMN role TYPE user_role_old
                    USING CASE role
                        WHEN '0' THEN 'admin'
                        WHEN '1' THEN 'caixa'
                        WHEN '2' THEN 'cozinha'
                        ELSE role::text
                    END::user_role_old;

                DROP TYPE user_role;
                ALTER TYPE user_role_old RENAME TO user_role;
            ELSIF has_text THEN
                NULL;
            ELSE
                BEGIN
                    CREATE TYPE user_role AS ENUM ('admin', 'caixa', 'cozinha');
                EXCEPTION
                    WHEN duplicate_object THEN NULL;
                END;
            END IF;
        END
        $$;
        """
    )
