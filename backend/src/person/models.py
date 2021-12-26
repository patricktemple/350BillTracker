import enum
from uuid import uuid4

from sqlalchemy import Column, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import foreign, relationship, remote

from ..models import TIMESTAMP, UUID, db

# TODO: Fix all eager loading


class Person(db.Model):
    __tablename__ = "persons"

    class PersonType(enum.Enum):
        COUNCIL_MEMBER = 1
        ASSEMBLY_MEMBER = 2
        SENATOR = 3
        STAFFER = 4

    # This is the internal ID shared by all people
    id = Column(UUID, primary_key=True, default=uuid4)

    name = Column(Text, nullable=False)
    title = Column(Text)
    email = Column(Text)
    phone = Column(Text)

    twitter = Column(Text)  # excludes the @ symbol

    # Track our own info on the person
    notes = Column(Text)

    type = Column(Enum(PersonType), nullable=False)
    council_member = relationship(
        "CouncilMember", back_populates="person", uselist=False
    )
    senator = relationship("Senator", back_populates="person", uselist=False)
    assembly_member = relationship(
        "AssemblyMember", back_populates="person", uselist=False
    )

    # These are added by our static data
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
    __tablename__ = "council_members"

    # Foreign key to Person parent table
    # Possibly we want to add "lazy=joined" below and on all similar relationships
    person_id = Column(UUID, ForeignKey(Person.id), primary_key=True)

    # ID of the City Council API object, which is also called Person
    city_council_person_id = Column(
        Integer, nullable=False, index=True, unique=True
    )  # index maybe?

    term_start = Column(TIMESTAMP)
    term_end = Column(TIMESTAMP)

    # District phone is stored in Person.phone
    legislative_phone = Column(Text)

    sponsorships = relationship(
        "CitySponsorship", back_populates="council_member"
    )

    person = relationship("Person", back_populates="council_member")

    borough = Column(Text)
    website = Column(Text)


class Senator(db.Model):
    __tablename__ = "senators"

    # Foreign key to Person parent table
    person_id = Column(UUID, ForeignKey(Person.id), primary_key=True)
    person = relationship("Person", back_populates="senator")
    sponsorships = relationship("SenateSponsorship", back_populates="senator")


class AssemblyMember(db.Model):
    __tablename__ = "assembly_members"

    # Foreign key to Person parent table
    person_id = Column(UUID, ForeignKey(Person.id), primary_key=True)
    person = relationship("Person", back_populates="assembly_member")

    sponsorships = relationship(
        "AssemblySponsorship", back_populates="assembly_member"
    )


# Staffers have a single boss. They're one to many.
class Staffer(db.Model):
    __tablename__ = "staffers_2"

    # Can I configure all these "subtypes" to automatically fetch their parent data?

    # ID of the person themselves:
    person_id = Column(UUID, ForeignKey(Person.id), primary_key=True)

    boss_id = Column(UUID, ForeignKey(Person.id), nullable=False, index=True)

    person = relationship(
        "Person", foreign_keys=[person_id], back_populates="staffer"
    )
    boss = relationship(
        "Person", foreign_keys=[boss_id], back_populates="staffers"
    )

    @property
    def display_string(self):
        contact_methods = [self.phone, self.email, self.display_twitter]
        contact_methods = [c for c in contact_methods if c]
        contact_string = ", ".join(contact_methods)
        if not contact_string:
            contact_string = "No contact info"
        title_string = f"{self.title} - " if self.title else ""
        return f"{title_string}{self.name} ({contact_string})"


Person.staffer = relationship(
    Staffer,
    foreign_keys=[Staffer.person_id],
    back_populates="person",
    uselist=False,
)
Person.staffers = relationship(
    "Staffer", foreign_keys=[Staffer.boss_id], back_populates="boss"
)

# This naming is SO confusing!!! Do better than this. Maybe call Senator/Staffer etc "SenatorInfo" or "SenatorDetails" or something like that?
Person.staffer_person = relationship(
    Person,
    secondary="staffers_2",
    primaryjoin=Person.id == Staffer.person_id,
    secondaryjoin=Staffer.boss_id == Person.id,
    back_populates="staffer_persons",
    viewonly=True,
)
Person.staffer_persons = relationship(
    Person,
    secondary="staffers_2",
    primaryjoin=Person.id == Staffer.boss_id,
    secondaryjoin=Staffer.person_id == Person.id,
    back_populates="staffer_person",
    viewonly=True,
)
