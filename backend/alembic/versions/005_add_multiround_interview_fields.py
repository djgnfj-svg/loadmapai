"""Add multi-round interview fields

Revision ID: 005
Revises: 004
Create Date: 2024-01-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new enum value for InterviewStatus
    op.execute("ALTER TYPE interviewstatus ADD VALUE IF NOT EXISTS 'terminated'")
    
    # Add multi-round tracking columns
    op.add_column('interview_sessions', sa.Column('current_round', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('interview_sessions', sa.Column('max_rounds', sa.Integer(), nullable=True, server_default='3'))
    
    # Add all questions and answers columns
    op.add_column('interview_sessions', sa.Column('all_questions', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('interview_sessions', sa.Column('all_answers', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('interview_sessions', sa.Column('evaluations', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
    
    # Add invalid tracking columns
    op.add_column('interview_sessions', sa.Column('invalid_history', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('interview_sessions', sa.Column('invalid_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('interview_sessions', sa.Column('consecutive_invalid', sa.Integer(), nullable=True, server_default='0'))
    
    # Add termination columns
    op.add_column('interview_sessions', sa.Column('is_terminated', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('interview_sessions', sa.Column('termination_reason', sa.String(200), nullable=True))
    op.add_column('interview_sessions', sa.Column('warning_message', sa.Text(), nullable=True))
    
    # Update defaults to not null
    op.alter_column('interview_sessions', 'current_round', nullable=False, server_default=None)
    op.alter_column('interview_sessions', 'max_rounds', nullable=False, server_default=None)
    op.alter_column('interview_sessions', 'all_questions', nullable=False, server_default=None)
    op.alter_column('interview_sessions', 'all_answers', nullable=False, server_default=None)
    op.alter_column('interview_sessions', 'evaluations', nullable=False, server_default=None)
    op.alter_column('interview_sessions', 'invalid_history', nullable=False, server_default=None)
    op.alter_column('interview_sessions', 'invalid_count', nullable=False, server_default=None)
    op.alter_column('interview_sessions', 'consecutive_invalid', nullable=False, server_default=None)
    op.alter_column('interview_sessions', 'is_terminated', nullable=False, server_default=None)


def downgrade() -> None:
    op.drop_column('interview_sessions', 'warning_message')
    op.drop_column('interview_sessions', 'termination_reason')
    op.drop_column('interview_sessions', 'is_terminated')
    op.drop_column('interview_sessions', 'consecutive_invalid')
    op.drop_column('interview_sessions', 'invalid_count')
    op.drop_column('interview_sessions', 'invalid_history')
    op.drop_column('interview_sessions', 'evaluations')
    op.drop_column('interview_sessions', 'all_answers')
    op.drop_column('interview_sessions', 'all_questions')
    op.drop_column('interview_sessions', 'max_rounds')
    op.drop_column('interview_sessions', 'current_round')
    # Note: Cannot remove enum value in PostgreSQL without recreating the type
