"""create min_bar_data

Revision ID: 20be9ab6ec3f
Revises: e9c03fc949ad
Create Date: 2022-04-11 00:30:55.284202

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20be9ab6ec3f'
down_revision = 'e9c03fc949ad'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'min_bar_data',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('symbol', sa.Text()),
        sa.Column('timestamp', sa.DateTime()),
        sa.Column('open', sa.Float()),
        sa.Column('high', sa.Float()),
        sa.Column('low', sa.Float()),
        sa.Column('close', sa.Float()),
        sa.Column('volume', sa.Integer())
    )

    op.create_table(
        'news_data',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbols', postgresql.ARRAY(sa.String)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('headline', sa.Text()),
        sa.Column('summary', sa.Text()),
        sa.Column('content', sa.Text()),
        sa.Column('author', sa.Text()),
        sa.Column('url', sa.Text()),
        sa.Column('source', sa.Text())
    )


def downgrade():
    op.drop_table('min_bar_data')
    op.drop_table('news_data')
