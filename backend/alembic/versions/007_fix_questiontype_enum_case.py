"""fix questiontype enum case to uppercase

Revision ID: 007
Revises: 006
Create Date: 2025-12-11

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL enum 값 변경: 소문자 -> 대문자
    # 1. 새 enum 타입 생성
    op.execute("""
        CREATE TYPE questiontype_new AS ENUM ('ESSAY', 'MULTIPLE_CHOICE', 'SHORT_ANSWER');
    """)

    # 2. 기존 컬럼을 새 타입으로 변환
    op.execute("""
        ALTER TABLE questions
        ALTER COLUMN question_type TYPE questiontype_new
        USING (
            CASE question_type::text
                WHEN 'essay' THEN 'ESSAY'
                WHEN 'multiple_choice' THEN 'MULTIPLE_CHOICE'
                WHEN 'short_answer' THEN 'SHORT_ANSWER'
                ELSE question_type::text
            END
        )::questiontype_new;
    """)

    # 3. 기존 enum 타입 삭제
    op.execute("DROP TYPE questiontype;")

    # 4. 새 enum 타입 이름을 원래 이름으로 변경
    op.execute("ALTER TYPE questiontype_new RENAME TO questiontype;")


def downgrade() -> None:
    # 대문자 -> 소문자로 원복
    op.execute("""
        CREATE TYPE questiontype_old AS ENUM ('essay', 'multiple_choice', 'short_answer');
    """)

    op.execute("""
        ALTER TABLE questions
        ALTER COLUMN question_type TYPE questiontype_old
        USING (
            CASE question_type::text
                WHEN 'ESSAY' THEN 'essay'
                WHEN 'MULTIPLE_CHOICE' THEN 'multiple_choice'
                WHEN 'SHORT_ANSWER' THEN 'short_answer'
                ELSE question_type::text
            END
        )::questiontype_old;
    """)

    op.execute("DROP TYPE questiontype;")
    op.execute("ALTER TYPE questiontype_old RENAME TO questiontype;")
