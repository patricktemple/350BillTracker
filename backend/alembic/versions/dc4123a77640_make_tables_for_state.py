"""Make tables for state

Revision ID: dc4123a77640
Revises: a33750368a20
Create Date: 2021-12-19 13:44:38.321277

"""
from alembic import op
import sqlalchemy as sa
import src
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dc4123a77640'
down_revision = 'a33750368a20'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('persons',
    sa.Column('id', src.models.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('email', sa.Text(), nullable=True),
    sa.Column('phone', sa.Text(), nullable=True),
    sa.Column('twitter', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('CITY_COUNCIL_MEMBER', 'STATE_ASSEMBLY_MEMBER', 'STATE_SENATOR', 'STAFFER', name='persontype'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('city_bills',
    sa.Column('bill_id', src.models.UUID(as_uuid=True), nullable=False),
    sa.Column('file', sa.Text(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('intro_date', src.models.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('status', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['bills.id'], ),
    sa.PrimaryKeyConstraint('bill_id')
    )
    op.create_table('city_council_members',
    sa.Column('person_id', src.models.UUID(as_uuid=True), nullable=False),
    sa.Column('city_council_person_id', sa.Integer(), nullable=False),
    sa.Column('term_start', src.models.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('term_end', src.models.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('legislative_phone', sa.Text(), nullable=True),
    sa.Column('borough', sa.Text(), nullable=True),
    sa.Column('website', sa.Text(), nullable=True),
    sa.Column('party', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ),
    sa.PrimaryKeyConstraint('person_id')
    )
    op.create_table('state_assembly_members',
    sa.Column('person_id', src.models.UUID(as_uuid=True), nullable=False),
    sa.Column('party', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ),
    sa.PrimaryKeyConstraint('person_id')
    )
    op.create_table('state_bills',
    sa.Column('bill_id', src.models.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['bills.id'], ),
    sa.PrimaryKeyConstraint('bill_id')
    )
    op.create_table('state_senators',
    sa.Column('person_id', src.models.UUID(as_uuid=True), nullable=False),
    sa.Column('party', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ),
    sa.PrimaryKeyConstraint('person_id')
    )
    op.create_table('city_sponsorships',
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('city_council_member_id', sa.Integer(), nullable=False),
    sa.Column('sponsor_sequence', sa.Integer(), nullable=True),
    sa.Column('added_at', src.models.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['bill_id'], ['city_bills.bill_id'], ),
    sa.ForeignKeyConstraint(['city_council_member_id'], ['city_council_members.person_id'], ),
    sa.PrimaryKeyConstraint('bill_id', 'city_council_member_id')
    )
    op.create_table('state_assembly_bill_versions',
    sa.Column('id', src.models.UUID(as_uuid=True), nullable=False),
    sa.Column('bill_id', src.models.UUID(as_uuid=True), nullable=True),
    sa.Column('version_name', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['state_bills.bill_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_state_assembly_bill_versions_bill_id'), 'state_assembly_bill_versions', ['bill_id'], unique=False)
    op.create_table('state_senate_bill_versions',
    sa.Column('id', src.models.UUID(as_uuid=True), nullable=False),
    sa.Column('bill_id', src.models.UUID(as_uuid=True), nullable=True),
    sa.Column('version_name', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['state_bills.bill_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_state_senate_bill_versions_bill_id'), 'state_senate_bill_versions', ['bill_id'], unique=False)
    op.create_table('state_assembly_sponsorships',
    sa.Column('id', src.models.UUID(as_uuid=True), nullable=False),
    sa.Column('assembly_version_id', sa.Integer(), nullable=False),
    sa.Column('assembly_member_id', src.models.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['assembly_member_id'], ['state_senators.person_id'], ),
    sa.ForeignKeyConstraint(['assembly_version_id'], ['state_assembly_bill_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('state_senate_sponsorships',
    sa.Column('id', src.models.UUID(as_uuid=True), nullable=False),
    sa.Column('senate_version_id', sa.Integer(), nullable=False),
    sa.Column('senator_id', src.models.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['senate_version_id'], ['state_senate_bill_versions.id'], ),
    sa.ForeignKeyConstraint(['senator_id'], ['state_senators.person_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('legislators')
    op.drop_table('bill_sponsorships')
    op.add_column('bills', sa.Column('type', sa.Enum('CITY', 'STATE', name='billtype'), nullable=False))
    op.drop_column('bills', 'title')
    op.drop_column('bills', 'body')
    op.drop_column('bills', 'status')
    op.drop_column('bills', 'file')
    op.drop_column('bills', 'intro_date')
    op.add_column('staffers', sa.Column('person_id', src.models.UUID(as_uuid=True), nullable=False))
    op.add_column('staffers', sa.Column('boss_id', src.models.UUID(as_uuid=True), nullable=False))
    op.create_index(op.f('ix_staffers_boss_id'), 'staffers', ['boss_id'], unique=False)
    op.drop_constraint('staffers_legislator_id_fkey', 'staffers', type_='foreignkey')
    op.create_foreign_key(None, 'staffers', 'persons', ['person_id'], ['id'])
    op.create_foreign_key(None, 'staffers', 'persons', ['boss_id'], ['id'])
    op.drop_column('staffers', 'title')
    op.drop_column('staffers', 'twitter')
    op.drop_column('staffers', 'id')
    op.drop_column('staffers', 'name')
    op.drop_column('staffers', 'email')
    op.drop_column('staffers', 'phone')
    op.drop_column('staffers', 'legislator_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('staffers', sa.Column('legislator_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('staffers', sa.Column('phone', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('staffers', sa.Column('email', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('staffers', sa.Column('name', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('staffers', sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False))
    op.add_column('staffers', sa.Column('twitter', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('staffers', sa.Column('title', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'staffers', type_='foreignkey')
    op.drop_constraint(None, 'staffers', type_='foreignkey')
    op.create_foreign_key('staffers_legislator_id_fkey', 'staffers', 'legislators', ['legislator_id'], ['id'])
    op.drop_index(op.f('ix_staffers_boss_id'), table_name='staffers')
    op.drop_column('staffers', 'boss_id')
    op.drop_column('staffers', 'person_id')
    op.add_column('bills', sa.Column('intro_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))
    op.add_column('bills', sa.Column('file', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('bills', sa.Column('status', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('bills', sa.Column('body', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('bills', sa.Column('title', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_column('bills', 'type')
    op.create_table('bill_sponsorships',
    sa.Column('bill_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('legislator_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('added_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('sponsor_sequence', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['bill_id'], ['bills.id'], name='bill_sponsorships_bill_id_fkey'),
    sa.ForeignKeyConstraint(['legislator_id'], ['legislators.id'], name='bill_sponsorships_legislator_id_fkey'),
    sa.PrimaryKeyConstraint('bill_id', 'legislator_id', name='bill_sponsorships_pkey')
    )
    op.create_table('legislators',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('term_start', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('term_end', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('email', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('district_phone', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('legislative_phone', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('borough', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('website', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('twitter', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('party', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='legislators_pkey')
    )
    op.drop_table('state_senate_sponsorships')
    op.drop_table('state_assembly_sponsorships')
    op.drop_index(op.f('ix_state_senate_bill_versions_bill_id'), table_name='state_senate_bill_versions')
    op.drop_table('state_senate_bill_versions')
    op.drop_index(op.f('ix_state_assembly_bill_versions_bill_id'), table_name='state_assembly_bill_versions')
    op.drop_table('state_assembly_bill_versions')
    op.drop_table('city_sponsorships')
    op.drop_table('state_senators')
    op.drop_table('state_bills')
    op.drop_table('state_assembly_members')
    op.drop_table('city_council_members')
    op.drop_table('city_bills')
    op.drop_table('persons')
    # ### end Alembic commands ###
