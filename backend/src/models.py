from uuid import uuid4

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Text,
    TypeDecorator,
    sql,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import TIMESTAMP as _TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as _UUID
from sqlalchemy.orm import relationship

from .app import app
from .utils import now

import enum

db = SQLAlchemy(app)


class UUID(TypeDecorator):
    impl = _UUID(as_uuid=True)


class TIMESTAMP(TypeDecorator):
    impl = _TIMESTAMP(timezone=True)


DEFAULT_TWITTER_SEARCH_TERMS = [
    "solar",
    "climate",
    "wind power",
    "renewable",
    "fossil fuel",
]

class Party(enum.Enum):
    DEMOCRATIC = 1
    REPUBLICAN = 2
    OTHER = 3


# TODO: Figure out all indexes


# Bills -------------------------------------------------------


class Bill(db.Model):
    __tablename__ = "bills"

    class BillType(enum.Enum):
        CITY = 1
        STATE = 2

    id = Column(UUID, primary_key=True)
    name = Column(Text, nullable=False)

    # Info on child objects:
    type = Column(BillType, nullable=False)
    city_bill = relationship("CityBill", back_populates="bill", uselist=False)
    state_bill = relationship("StateBill", back_populates="bill", uselist=False)

    # Data we track
    notes = Column(Text, nullable=False, server_default="")
    nickname = Column(Text, nullable=False, server_default="")
    twitter_search_terms = Column(
        ARRAY(Text), nullable=False, default=DEFAULT_TWITTER_SEARCH_TERMS
    )

    power_hours = relationship(
        "PowerHour", back_populates="bill", cascade="all, delete"
    )
    attachments = relationship(
        "BillAttachment", back_populates="bill", cascade="all, delete"
    )


    @property
    def display_name(self):
        return self.nickname if self.nickname else self.name


# TODO: This model is more complicated, more correct for maintenance but maybe will take
# longer to develop on short term. After making the model, look into whether a flat structure
# all in the same table is much more straightforward.


class CityBill(db.Model):
    __tablename__ = "city_bills"

    bill_id = Column(UUID, ForeignKey(Bill.id), primary_key=True)

    file = Column(Text, nullable=False)  # e.g. Int 2317-2021

    bill = relationship("Bill", back_populates="city_bill")

    title = Column(Text, nullable=False)

    intro_date = Column(TIMESTAMP, nullable=False)

    status = Column(Text, nullable=False) # ??? here or in subclass?

    # Question: should bill sponsorships exict on the parent bill or on each type of bill?
    sponsorships = relationship(
        "CitySponsorship", back_populates="bill", cascade="all, delete"
    )
    
    @property
    def tracked(self):
        return True


class StateBill(db.Model):
    __tablename__ = "state_bills"

    bill_id = Column(UUID, ForeignKey(Bill.id), primary_key=True)


class StateSenateBillVersion(db.Model):
    __table__ = "state_senate_bill_versions"

    id = Column(UUID, primary_key=True)
    bill_id = Column(UUID, ForeignKey(StateBill.id))
    version_name = Column(Text, nullable=False)


class StateAssemblyBillVersion(db.Model):
    # Use a base class for this and senate versions, maybe? and same for sponsorships
    __table__ = "state_assembly_bill_versions"

    id = Column(UUID, primary_key=True)
    bill_id = Column(UUID, ForeignKey(StateBill.id))
    version_name = Column(Text, nullable=False)


# Person -------------------------------------------------------------


class Person(db.Model):
    __tablename__= "persons"

    class PersonType(enum.Enum):
        CITY_COUNCIL_MEMBER = 1
        STATE_ASSEMBLY_MEMBER = 2
        STATE_SENATOR = 3
        STAFFER = 4 # this might be problematic...

    # This is the internal ID shared by all people
    id = Column(UUID, primary_key=True)

    name = Column(Text, nullable=False)
    title = Column(Text)
    email = Column(Text)
    phone = Column(Text)

    twitter = Column(Text)  # excludes the @ symbol

    # Track our own info on the person
    notes = Column(Text)

    type = Column(PersonType, nullable=False)
    city_council_member = relationship("CityCouncilMember", back_populates="person", uselist=False)
    staffer = relationship("Staffer", primaryjoin="Staffer.person_id == Person.id", back_populates="person", uselist=False)

    staffers = relationship("Staffer", primaryjoin="Staffer.boss_id == Person.id", back_populates="boss")

    @property
    def display_twitter(self):
        return "@" + self.twitter if self.twitter else None

    @property
    def twitter_url(self):
        return (
            f"https://www.twitter.com/{self.twitter}" if self.twitter else None
        )


class CityCouncilMember(db.Model):
    __tablename__ = "city_council_members"

    # Foreign key to Person parent table
    person_id = Column(UUID, ForeignKey(Person.id), nullable=False)

    # ID of the City Council API object, which is also called Person
    city_council_person_id = Column(Integer, nullable=False) # index maybe?

    term_start = Column(TIMESTAMP)
    term_end = Column(TIMESTAMP)

    # District phone is stored in Person.phone
    legislative_phone = Column(Text)

    sponsorships = relationship("CitySponsorship", back_populates="city_council_member")

    person = relationship("Person")

    borough = Column(Text)
    website = Column(Text)

    # These are added by our static data
    party = Column(Text)



class StateSenator(db.Model):
    __tablename__ = "state_senators"

    # Foreign key to Person parent table
    person_id = Column(UUID, ForeignKey(Person.id), nullable=False)

    # These are added by our static data
    party = Column(Text)



class StateAssemblyMember(db.Model):
    __tablename__ = "state_assembly_members"

    # Foreign key to Person parent table
    person_id = Column(UUID, ForeignKey(Person.id), nullable=False)

    # These are added by our static data
    party = Column(Text)


# Staffers have a single boss. They're one to many.
class Staffer(db.Model):
    __tablename__ = "staffers"

    # Can I configure all these "subtypes" to automatically fetch their parent data?

    # ID of the person themselves:
    person_id = Column(UUID, ForeignKey=Person.id, primary_key=True)

    boss_id = Column(UUID, ForeignKey=Person.id, nullable=False, index=True)

    person = relationship("Person", primarjoin=lambda: Staffer.person_id == Person.id, back_populates="staffer")
    boss = relationship("Person", primaryjoin=lambda: Staffer.boss_id == Person.id, back_populates="staffers")

    @property
    def display_string(self):
        contact_methods = [self.phone, self.email, self.display_twitter]
        contact_methods = [c for c in contact_methods if c]
        contact_string = ", ".join(contact_methods)
        if not contact_string:
            contact_string = "No contact info"
        title_string = f"{self.title} - " if self.title else ""

        return f"{title_string}{self.name} ({contact_string})"


# Sponsorships -----------------------------------------------------


class CitySponsorship(db.Model):
    __tablename__ = "city_sponsorships"

    bill_id = Column(
        Integer, ForeignKey("city_bills.bill_id"), nullable=False, primary_key=True
    )
    city_bill = relationship(
        "Bill", back_populates="sponsorships", order_by="Bill.name"
    )

    city_council_member_id = Column(
        Integer, ForeignKey("city_council_members.person_id"), nullable=False, primary_key=True
    )
    city_council_member = relationship(
        "CityCouncilMember", back_populates="sponsorships", order_by="CityCouncilMember.name" # ugh --- this should order by Person.name?
    )
    # TODO: Make this nullable=false once cron has run in prod and backfilled
    sponsor_sequence = Column(Integer, nullable=True)

    # The timestamp when we first saw this sponsorship in the bill's list.
    # This is a proxy for when the sponsor actually signed on to the bill.
    # Note that when we first start tracking a bill, it may already have sponsorships
    # and we don't know the date that those were added. We leave added_at as null,
    # in that case, and only fill this in for sponsorships that were added later on.
    added_at = Column(TIMESTAMP)


class StateSenateSponsorship(db.Model):
    __tablename__ = "state_senate_sponsorships"

    id = Column(UUID, primary_key=True)

    senate_version_id = Column(
        Integer, ForeignKey(StateSenateBillVersion.id), nullable=False
    )
    senate_version = relationship(
        "StateSenateBillVersion", back_populates="sponsorships"# , order_by="Bill.name"
    )

    senator_id = Column(
        UUID, ForeignKey(StateSenator.person_id), nullable=False
    )
    senator = relationship(
        StateSenator, back_populates="sponsorships" #
    )

    # # TODO: Make this nullable=false once cron has run in prod and backfilled
    # sponsor_sequence = Column(Integer, nullable=True)

    # # The timestamp when we first saw this sponsorship in the bill's list.
    # # This is a proxy for when the sponsor actually signed on to the bill.
    # # Note that when we first start tracking a bill, it may already have sponsorships
    # # and we don't know the date that those were added. We leave added_at as null,
    # # in that case, and only fill this in for sponsorships that were added later on.
    # added_at = Column(TIMESTAMP)


class StateAssemblySponsorship(db.Model):
    __tablename__ = "state_assembly_sponsorships"

    id = Column(UUID, primary_key=True)

    assembly_version_id = Column(
        Integer, ForeignKey(StateAssemblyBillVersion.id), nullable=False
    )
    assembly_version = relationship(
        StateAssemblyBillVersion, back_populates="sponsorships"# , order_by="Bill.name"
    )

    assembly_member_id = Column(
        UUID, ForeignKey(StateSenator.person_id), nullable=False
    )
    assembly_member = relationship(
        StateSenator, back_populates="sponsorships" #
    )

    # # TODO: Make this nullable=false once cron has run in prod and backfilled
    # sponsor_sequence = Column(Integer, nullable=True)

    # # The timestamp when we first saw this sponsorship in the bill's list.
    # # This is a proxy for when the sponsor actually signed on to the bill.
    # # Note that when we first start tracking a bill, it may already have sponsorships
    # # and we don't know the date that those were added. We leave added_at as null,
    # # in that case, and only fill this in for sponsorships that were added later on.
    # added_at = Column(TIMESTAMP)


# Bill attachments --------------------------------------------------


class BillAttachment(db.Model):
    __tablename__ = "bill_attachments"

    # TODO: Make this a UUID
    id = Column(Integer, primary_key=True)
    bill_id = Column(
        Integer, ForeignKey("bills.id"), nullable=False, index=True
    )
    bill = relationship("Bill", back_populates="attachments")

    name = Column(Text)
    url = Column(Text, nullable=False)


class PowerHour(db.Model):
    __tablename__ = "power_hours"

    id = Column(UUID, primary_key=True, default=uuid4)
    bill_id = Column(
        Integer, ForeignKey("bills.id"), nullable=False, index=True
    )

    title = Column(Text)
    spreadsheet_url = Column(Text, nullable=False)
    spreadsheet_id = Column(Text, nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, default=now)
    bill = relationship(
        "Bill", back_populates="power_hours"
    )



# Users --------------------------------------------


class User(db.Model):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, default=uuid4)

    email = Column(
        Text, index=True, nullable=False, unique=True
    )  # always lowercase
    name = Column(Text)

    login_links = relationship(
        "LoginLink", back_populates="user", cascade="all, delete"
    )

    # The "root" user can never be deleted.
    can_be_deleted = Column(Boolean, nullable=False, server_default=sql.true())

    send_bill_update_notifications = Column(
        Boolean, nullable=False, server_default=sql.false(), index=True
    )

    __table_args__ = (
        CheckConstraint(
            "email = lower(email)", name="check_email_is_lowercase"
        ),
    )


class LoginLink(db.Model):
    __tablename__ = "login_links"

    user_id = Column(UUID, ForeignKey(User.id), nullable=False)

    token = Column(Text, nullable=False, primary_key=True)

    expires_at = Column(TIMESTAMP, nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, default=now)

    user = relationship("User", back_populates="login_links")

    # TODO: Consider only allowing these links to be used once. Better security
    # in case of leaked browser URL, but worse UX.
