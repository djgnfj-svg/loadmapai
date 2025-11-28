"""Create interview_sessions table

Revision ID: 004
Revises: 003
Create Date: 2025-11-29
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
    # Create interview status enum
    interview_status = postgresql.ENUM(
        'in_progress', 'completed', 'abandoned',
        name='interviewstatus',
        create_type=False
    )
    interview_status.create(op.get_bind(), checkfirst=True)

    # Create interview_sessions table
    op.create_table(
        'interview_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),

        # Interview parameters
        sa.Column('topic', sa.String(200), nullable=False),
        sa.Column('mode', sa.String(20), nullable=False),
        sa.Column('duration_months', sa.Integer(), nullable=False),

        # Stage tracking
        sa.Column('current_stage', sa.Integer(), default=1, nullable=False),
        sa.Column('status', postgresql.ENUM('in_progress', 'completed', 'abandoned',
                                            name='interviewstatus', create_type=False),
                  default='in_progress', nullable=False),

        # Stage data (JSON)
        sa.Column('stage_data', postgresql.JSONB(), default={}, nullable=False),

        # Current stage working data
        sa.Column('current_questions', postgresql.JSONB(), default=[], nullable=False),
        sa.Column('current_answers', postgresql.JSONB(), default=[], nullable=False),
        sa.Column('current_evaluations', postgresql.JSONB(), default=[], nullable=False),

        # Follow-up tracking
        sa.Column('followup_count', sa.Integer(), default=0, nullable=False),
        sa.Column('pending_followup_questions', postgresql.JSONB(), default=[], nullable=False),
        sa.Column('max_followups_per_stage', sa.Integer(), default=2, nullable=False),

        # Compiled results
        sa.Column('compiled_context', sa.Text(), nullable=True),
        sa.Column('key_insights', postgresql.JSONB(), nullable=True),

        # Extracted schedule
        sa.Column('extracted_daily_minutes', sa.Integer(), nullable=True),
        sa.Column('extracted_rest_days', postgresql.JSONB(), nullable=True),
        sa.Column('extracted_intensity', sa.String(20), nullable=True),

        # Link to roadmap
        sa.Column('roadmap_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('roadmaps.id', ondelete='SET NULL'), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create indexes
    op.create_index('ix_interview_sessions_user_id', 'interview_sessions', ['user_id'])
    op.create_index('ix_interview_sessions_status', 'interview_sessions', ['status'])


def downgrade() -> None:
    op.drop_index('ix_interview_sessions_status', table_name='interview_sessions')
    op.drop_index('ix_interview_sessions_user_id', table_name='interview_sessions')
    op.drop_table('interview_sessions')

    # Drop enum type
    interview_status = postgresql.ENUM(
        'in_progress', 'completed', 'abandoned',
        name='interviewstatus'
    )
    interview_status.drop(op.get_bind(), checkfirst=True)
