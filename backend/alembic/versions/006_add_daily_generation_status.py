"""add_daily_generation_status

Revision ID: 006
Revises: f825b454faf5
Create Date: 2025-12-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = 'f825b454faf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # dailygenerationstatus enum 생성
    op.execute('''
        DO $$ BEGIN
            CREATE TYPE dailygenerationstatus AS ENUM ('none', 'generating', 'completed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    ''')

    # weekly_tasks 테이블에 daily_generation_status 컬럼 추가
    op.add_column(
        'weekly_tasks',
        sa.Column(
            'daily_generation_status',
            sa.Enum('none', 'generating', 'completed', name='dailygenerationstatus'),
            server_default='none',
            nullable=False
        )
    )


def downgrade() -> None:
    op.drop_column('weekly_tasks', 'daily_generation_status')
    op.execute('DROP TYPE IF EXISTS dailygenerationstatus')
