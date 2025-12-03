"""add_daily_goals_table

Revision ID: 7bc28bdb9ff9
Revises: 004
Create Date: 2025-12-03 02:22:49.356210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7bc28bdb9ff9'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('daily_goals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('weekly_task_id', sa.UUID(), nullable=False),
        sa.Column('day_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['weekly_task_id'], ['weekly_tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('daily_goals')
