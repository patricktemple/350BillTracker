"""Add created_at to login link

Revision ID: e00f4caa87a9
Revises: 2cae43acc501
Create Date: 2021-10-01 23:39:18.190189

"""
from alembic import op
import sqlalchemy as sa
import src


# revision identifiers, used by Alembic.
revision = 'e00f4caa87a9'
down_revision = '2cae43acc501'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('login_links', sa.Column('created_at', src.models.TIMESTAMP(timezone=True), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('login_links', 'created_at')
    # ### end Alembic commands ###
