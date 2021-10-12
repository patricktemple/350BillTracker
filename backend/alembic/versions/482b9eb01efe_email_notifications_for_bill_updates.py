"""Email notifications for bill updates

Revision ID: 482b9eb01efe
Revises: c0a643362ad9
Create Date: 2021-10-12 09:57:34.886627

"""
from alembic import op
import sqlalchemy as sa
import src


# revision identifiers, used by Alembic.
revision = '482b9eb01efe'
down_revision = 'c0a643362ad9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bill_sponsorships', sa.Column('added_at', src.models.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('users', sa.Column('send_bill_update_notifications', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'send_bill_update_notifications')
    op.drop_column('bill_sponsorships', 'added_at')
    # ### end Alembic commands ###
