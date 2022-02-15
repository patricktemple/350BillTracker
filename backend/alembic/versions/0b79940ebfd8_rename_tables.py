"""Rename tables

Revision ID: 0b79940ebfd8
Revises: f84b802082d4
Create Date: 2021-12-26 10:54:44.320323

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

import src
from alembic import op

# revision identifiers, used by Alembic.
revision = "0b79940ebfd8"
down_revision = "f84b802082d4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE bills_2 RENAME TO bills;")
    op.execute("ALTER TABLE bill_attachments_2 RENAME TO bill_attachments;")
    op.execute("ALTER TABLE staffers_2 RENAME TO staffers;")
    op.execute("ALTER TABLE power_hours_2 RENAME TO power_hours;")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
