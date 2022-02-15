"""Add static data

Revision ID: 65c13df197c5
Revises: cf8896090d1d
Create Date: 2021-09-29 14:02:50.105564

"""
import sqlalchemy as sa

import src
from alembic import op

# revision identifiers, used by Alembic.
revision = "65c13df197c5"
down_revision = "cf8896090d1d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("legislators", sa.Column("party", sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("legislators", "party")
    # ### end Alembic commands ###
