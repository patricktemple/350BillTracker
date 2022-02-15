import enum
from typing import Union
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ..models import TIMESTAMP, UUID, db


class Person(db.Model):
    """
    Base table for every kind of person we track. General info shared by all
    people, such as name and phone, are kept here.

    A person is polymorphic. There is also a "type" that specifies which kind
    of person this is (such as a senator), and there are
    separate tables for each type of person that has more specific details.
    """

    __tablename__ = "persons"

    class PersonType(enum.Enum):
        # City
        COUNCIL_MEMBER = 1

        # State
        ASSEMBLY_MEMBER = 2
        SENATOR = 3

        # General
        STAFFER = 4

    # This is the internal ID shared by all people
    id = Column(UUID, primary_key=True, default=uuid4)

    name = Column(Text, nullable=False)
    title = Column(Text)
    email = Column(Text)

    twitter = Column(Text)  # excludes the @ symbol

    # Track our own info on the person
    notes = Column(Text)

    type = Column(Enum(PersonType), nullable=False)

    # If this person is a council member, points to the object that has more specific
    # details about them in that role.
    council_member = relationship(
        "CouncilMember", back_populates="person", uselist=False, lazy="joined"
    )

    # If this person is a state senator, points to the object that has more specific
    # details about them in that role.
    senator = relationship(
        "Senator", back_populates="person", uselist=False, lazy="joined"
    )

    # If this person is a state assembly, points to the object that has more specific
    # details about them in that role.
    assembly_member = relationship(
        "AssemblyMember", back_populates="person", uselist=False, lazy="joined"
    )

    office_contacts = relationship(
        "OfficeContact", back_populates="person", cascade="all, delete-orphan"
    )

    # These are added by our static data
    # TODO: Make this an enum?
    party = Column(Text)

    @property
    def display_twitter(self):
        return "@" + self.twitter if self.twitter else None

    @property
    def twitter_url(self):
        return (
            f"https://www.twitter.com/{self.twitter}" if self.twitter else None
        )


class CouncilMember(db.Model):
    """
    Data about a specific council member. For each row in this there must also
    be a Person that has more general info about this person, such as name.
    """

    __tablename__ = "council_members"

    # Foreign key to Person parent table
    person_id = Column(UUID, ForeignKey(Person.id), primary_key=True)

    # ID of the City Council API object, which is also called Person
    city_council_person_id = Column(
        Integer, nullable=False, index=True, unique=True
    )

    term_start = Column(TIMESTAMP)
    term_end = Column(TIMESTAMP)

    sponsorships = relationship(
        "CitySponsorship", back_populates="council_member"
    )

    # The parent Person object.
    person = relationship(
        "Person", back_populates="council_member", lazy="joined"
    )

    borough = Column(Text)
    website = Column(Text)

    committee_memberships = relationship(
        "CouncilCommitteeMembership",
        back_populates="council_member",
        cascade="all, delete-orphan",
    )


class StateRepresentativeMixin:

    # Foreign key to Person parent table
    @declared_attr
    def person_id(self):
        return Column(UUID, ForeignKey(Person.id), primary_key=True)

    district = Column(Integer)

    state_member_id = Column(Integer, nullable=False, unique=True)


class Senator(db.Model, StateRepresentativeMixin):
    """
    Data about a specific state senator. For each row in this there must also
    be a Person that has more general info about this person, such as name.
    """

    __tablename__ = "senators"

    # The parent Person object.
    person = relationship("Person", back_populates="senator", lazy="joined")

    sponsorships = relationship(
        "SenateSponsorship",
        back_populates="representative",
        cascade="all, delete-orphan",
    )

    @property
    def website(self):
        return (
            f"https://www.nysenate.gov/district/{self.district}"
            if self.district
            else None
        )


class AssemblyMember(db.Model, StateRepresentativeMixin):
    """
    Data about a specific state assembly member. For each row in this there must
    also be a Person that has more general info about this person, such as name.
    """

    __tablename__ = "assembly_members"

    # The parent Person object.
    person = relationship(
        "Person", back_populates="assembly_member", lazy="joined"
    )

    sponsorships = relationship(
        "AssemblySponsorship",
        back_populates="representative",
        cascade="all, delete-orphan",
    )

    @property
    def website(self):
        return (
            f"https://nyassembly.gov/mem/?ad={self.district}"
            if self.district
            else None
        )


StateRepresentative = Union[Senator, AssemblyMember]


# Staffers have a single boss. They're one to many.
class Staffer(db.Model):
    __tablename__ = "staffers"

    # ID of the person themselves:
    person_id = Column(UUID, ForeignKey(Person.id), primary_key=True)

    boss_id = Column(UUID, ForeignKey(Person.id), nullable=False, index=True)

    # The Person object that represents general info about this person (NOT the person that
    # they work for.)
    person = relationship(
        "Person",
        foreign_keys=[person_id],
        back_populates="staffer",
        lazy="joined",
    )

    # The Person that this staffer works for.
    boss = relationship("Person", foreign_keys=[boss_id])


# If this person is a Staffer, gets the Staffer object that represents them.
Person.staffer = relationship(
    Staffer,
    foreign_keys=[Staffer.person_id],
    back_populates="person",
    cascade="all, delete",
    uselist=False,
)

# Gets all the Persons that work for this person as staffers.
Person.staffer_persons = relationship(
    Person,
    secondary="staffers",
    primaryjoin=Person.id == Staffer.boss_id,
    secondaryjoin=Staffer.person_id == Person.id,
    viewonly=True,
)


class OfficeContact(db.Model):
    __tablename__ = "office_contacts"

    class OfficeContactType(enum.Enum):
        CENTRAL_OFFICE = 1
        DISTRICT_OFFICE = 2
        OTHER = 3

    id = Column(UUID, primary_key=True, default=uuid4)

    person_id = Column(UUID, ForeignKey(Person.id), index=True, nullable=False)

    type = Column(Enum(OfficeContactType))

    phone = Column(Text)
    fax = Column(Text)
    city = Column(Text)

    person = relationship(
        "Person", back_populates="office_contacts", lazy="joined"
    )


class CouncilCommittee(db.Model):
    __tablename__ = "council_committees"

    id = Column(UUID, primary_key=True, default=uuid4)

    council_body_id = Column(Integer, nullable=False, index=True, unique=True)
    body_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    memberships = relationship(
        "CouncilCommitteeMembership",
        back_populates="committee",
        cascade="all, delete-orphan",
    )


class CouncilCommitteeMembership(db.Model):
    __tablename__ = "council_committee_memberships"

    id = Column(UUID, primary_key=True, default=uuid4)

    # Note this is the internal CouncilCommittee.id, not the city API's body ID
    # (which is CouncilCommittee.council_body_id).
    committee_id = Column(
        UUID, ForeignKey(CouncilCommittee.id), nullable=False, index=True
    )

    person_id = Column(
        UUID, ForeignKey(CouncilMember.person_id), nullable=False, index=True
    )
    is_chair = Column(Boolean, nullable=False, default=False)

    committee = relationship(
        CouncilCommittee, back_populates="memberships", lazy="joined"
    )
    council_member = relationship(
        CouncilMember, back_populates="committee_memberships", lazy="joined"
    )

    __table_args__ = (
        UniqueConstraint(
            "committee_id",
            "person_id",
            name="_council_committee_member_unique",
        ),
    )
