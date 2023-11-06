"""add content coulmn to post table

Revision ID: f21f3c4d080d
Revises: 36b71fc14fd1
Create Date: 2023-11-04 12:27:05.383852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f21f3c4d080d'
down_revision: Union[str, None] = '36b71fc14fd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
