"""Make login links single use

Revision ID: 1bcff1e81e30
Revises: c8f2969150b7
Create Date: 2022-03-04 23:53:56.173103

"""
from alembic import op
import sqlalchemy as sa
import src


# revision identifiers, used by Alembic.
revision = '1bcff1e81e30'
down_revision = 'c8f2969150b7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('login_links', sa.Column('used_at', src.models.TIMESTAMP(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('login_links', 'used_at')
    # ### end Alembic commands ###