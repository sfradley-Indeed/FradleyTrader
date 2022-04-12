"""modify news_data symbols to text

Revision ID: 79dd9de327e4
Revises: 20be9ab6ec3f
Create Date: 2022-04-11 20:23:18.456413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.dialects import postgresql

revision = '79dd9de327e4'
down_revision = '20be9ab6ec3f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('news_data', 'symbols', existing_type=sa.Text())


def downgrade():
    op.alter_column('news_data', 'symbols', existing_type=postgresql.ARRAY(sa.String))
