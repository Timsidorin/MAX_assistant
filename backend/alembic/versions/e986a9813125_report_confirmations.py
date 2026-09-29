"""report confirmations

Revision ID: e986a9813125
Revises: 6ed48971263d
Create Date: 2026-09-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e986a9813125'
down_revision: Union[str, Sequence[str], None] = '6ed48971263d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('reports', sa.Column('confirmations', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('reports', 'confirmations')
