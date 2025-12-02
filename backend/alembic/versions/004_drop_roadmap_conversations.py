"""drop roadmap_conversations table

Revision ID: 004
Revises: 003
Create Date: 2024-12-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop roadmap_conversations table (no longer used)
    op.drop_index('ix_roadmap_conversations_roadmap_id', table_name='roadmap_conversations')
    op.drop_table('roadmap_conversations')


def downgrade() -> None:
    # Recreate roadmap_conversations table
    op.create_table(
        'roadmap_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('roadmap_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roadmaps.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('target_type', sa.String(20), nullable=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('changes_applied', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_roadmap_conversations_roadmap_id', 'roadmap_conversations', ['roadmap_id'])
