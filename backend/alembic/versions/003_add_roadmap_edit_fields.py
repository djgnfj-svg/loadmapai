"""add roadmap edit fields

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # daily_tasks - add order field for multi-task per day
    op.add_column('daily_tasks', sa.Column('order', sa.Integer(), server_default='0', nullable=False))

    # roadmaps - add finalization fields
    op.add_column('roadmaps', sa.Column('is_finalized', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('roadmaps', sa.Column('finalized_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('roadmaps', sa.Column('edit_count_after_finalize', sa.Integer(), server_default='0', nullable=False))

    # roadmaps - add schedule fields
    op.add_column('roadmaps', sa.Column('daily_available_minutes', sa.Integer(), server_default='60', nullable=True))
    op.add_column('roadmaps', sa.Column('rest_days', postgresql.ARRAY(sa.Integer()), server_default='{}', nullable=True))
    op.add_column('roadmaps', sa.Column('intensity', sa.String(20), server_default='moderate', nullable=True))

    # Create roadmap_conversations table for AI chat history
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

    # Migrate existing ACTIVE roadmaps to is_finalized=true
    op.execute("UPDATE roadmaps SET is_finalized = true WHERE status = 'active'")


def downgrade() -> None:
    # Drop roadmap_conversations table
    op.drop_index('ix_roadmap_conversations_roadmap_id', table_name='roadmap_conversations')
    op.drop_table('roadmap_conversations')

    # Remove schedule fields from roadmaps
    op.drop_column('roadmaps', 'intensity')
    op.drop_column('roadmaps', 'rest_days')
    op.drop_column('roadmaps', 'daily_available_minutes')

    # Remove finalization fields from roadmaps
    op.drop_column('roadmaps', 'edit_count_after_finalize')
    op.drop_column('roadmaps', 'finalized_at')
    op.drop_column('roadmaps', 'is_finalized')

    # Remove order field from daily_tasks
    op.drop_column('daily_tasks', 'order')
