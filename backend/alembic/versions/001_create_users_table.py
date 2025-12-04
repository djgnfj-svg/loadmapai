"""create users table

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create auth_provider enum
    auth_provider_enum = postgresql.ENUM('EMAIL', 'GOOGLE', 'GITHUB', name='authprovider', create_type=False)
    auth_provider_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('auth_provider', auth_provider_enum, server_default='EMAIL', nullable=False),
        sa.Column('provider_id', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('users')

    # Drop enum type
    auth_provider_enum = postgresql.ENUM('EMAIL', 'GOOGLE', 'GITHUB', name='authprovider')
    auth_provider_enum.drop(op.get_bind(), checkfirst=True)
