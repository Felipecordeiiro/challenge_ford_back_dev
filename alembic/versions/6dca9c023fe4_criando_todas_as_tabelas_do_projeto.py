"""Criando todas as tabelas do projeto

Revision ID: 6dca9c023fe4
Revises: 
Create Date: 2025-03-20 03:53:27.872578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6dca9c023fe4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('vehicles',
        sa.Column('vehicle_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('prod_date', sa.DateTime(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('propulsion', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('vehicle_id')
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('vehicles')
