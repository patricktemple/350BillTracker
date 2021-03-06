"""Add committees

Revision ID: 633c4c780a33
Revises: 9fd6c4dbc2fe
Create Date: 2022-01-24 14:13:31.289865

"""
import sqlalchemy as sa

import src
from alembic import op

# revision identifiers, used by Alembic.
revision = "633c4c780a33"
down_revision = "9fd6c4dbc2fe"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "council_committees",
        sa.Column("id", src.models.UUID(as_uuid=True), nullable=False),
        sa.Column("council_body_id", sa.Integer(), nullable=False),
        sa.Column("body_type", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_council_committees_council_body_id"),
        "council_committees",
        ["council_body_id"],
        unique=True,
    )
    op.create_table(
        "council_committee_memberships",
        sa.Column("id", src.models.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "committee_id", src.models.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("person_id", src.models.UUID(as_uuid=True), nullable=False),
        sa.Column("is_chair", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["committee_id"],
            ["council_committees.id"],
        ),
        sa.ForeignKeyConstraint(
            ["person_id"],
            ["council_members.person_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "committee_id",
            "person_id",
            name="_council_committee_member_unique",
        ),
    )
    op.create_index(
        op.f("ix_council_committee_memberships_committee_id"),
        "council_committee_memberships",
        ["committee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_council_committee_memberships_person_id"),
        "council_committee_memberships",
        ["person_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_council_committee_memberships_person_id"),
        table_name="council_committee_memberships",
    )
    op.drop_index(
        op.f("ix_council_committee_memberships_committee_id"),
        table_name="council_committee_memberships",
    )
    op.drop_table("council_committee_memberships")
    op.drop_index(
        op.f("ix_council_committees_council_body_id"),
        table_name="council_committees",
    )
    op.drop_table("council_committees")
    # ### end Alembic commands ###
