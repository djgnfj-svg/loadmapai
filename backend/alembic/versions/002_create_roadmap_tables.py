"""create roadmap tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    roadmap_mode_enum = postgresql.ENUM('planning', 'learning', name='roadmapmode', create_type=False)
    roadmap_mode_enum.create(op.get_bind(), checkfirst=True)

    roadmap_status_enum = postgresql.ENUM('active', 'completed', 'paused', name='roadmapstatus', create_type=False)
    roadmap_status_enum.create(op.get_bind(), checkfirst=True)

    task_status_enum = postgresql.ENUM('pending', 'in_progress', 'completed', name='taskstatus', create_type=False)
    task_status_enum.create(op.get_bind(), checkfirst=True)

    # Create roadmaps table
    op.create_table(
        'roadmaps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('topic', sa.String(200), nullable=False),
        sa.Column('duration_months', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('mode', roadmap_mode_enum, server_default='planning', nullable=False),
        sa.Column('status', roadmap_status_enum, server_default='active', nullable=False),
        sa.Column('progress', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_roadmaps_user_id', 'roadmaps', ['user_id'])

    # Create monthly_goals table
    op.create_table(
        'monthly_goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('roadmap_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roadmaps.id', ondelete='CASCADE'), nullable=False),
        sa.Column('month_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', task_status_enum, server_default='pending', nullable=False),
        sa.Column('progress', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_monthly_goals_roadmap_id', 'monthly_goals', ['roadmap_id'])

    # Create weekly_tasks table
    op.create_table(
        'weekly_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('monthly_goal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('monthly_goals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', task_status_enum, server_default='pending', nullable=False),
        sa.Column('progress', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_weekly_tasks_monthly_goal_id', 'weekly_tasks', ['monthly_goal_id'])

    # Create daily_tasks table
    op.create_table(
        'daily_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('weekly_task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('weekly_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('day_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', task_status_enum, server_default='pending', nullable=False),
        sa.Column('is_checked', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_daily_tasks_weekly_task_id', 'daily_tasks', ['weekly_task_id'])


def downgrade() -> None:
    op.drop_table('daily_tasks')
    op.drop_table('weekly_tasks')
    op.drop_table('monthly_goals')
    op.drop_table('roadmaps')

    # Drop enums
    task_status_enum = postgresql.ENUM('pending', 'in_progress', 'completed', name='taskstatus')
    task_status_enum.drop(op.get_bind(), checkfirst=True)

    roadmap_status_enum = postgresql.ENUM('active', 'completed', 'paused', name='roadmapstatus')
    roadmap_status_enum.drop(op.get_bind(), checkfirst=True)

    roadmap_mode_enum = postgresql.ENUM('planning', 'learning', name='roadmapmode')
    roadmap_mode_enum.drop(op.get_bind(), checkfirst=True)
