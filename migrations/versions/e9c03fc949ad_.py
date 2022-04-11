"""Create bar data

Revision ID: e9c03fc949ad
Revises: bar_data table
Create Date: 2022-04-10 18:41:45.389354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9c03fc949ad'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'bar_data',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('symbol', sa.Text()),
        sa.Column('timestamp', sa.DateTime()),
        sa.Column('open', sa.Float()),
        sa.Column('high', sa.Float()),
        sa.Column('low', sa.Float()),
        sa.Column('close', sa.Float()),
        sa.Column('volume', sa.Integer()),
        sa.Column('trade_count', sa.Integer()),
        sa.Column('vwap', sa.Float())
    )


def downgrade():
    op.drop_table('bar_data')
