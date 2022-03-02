import enum
from uuid import uuid4

import flask
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, Text, sql
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import foreign, relationship, remote

from ..models import TIMESTAMP, UUID, db
from ..user.models import User
from ..utils import now

DEFAULT_TWITTER_SEARCH_TERMS = [
    "solar",
    "climate",
    "wind power",
    "renewable",
    "fossil fuel",
]


class StateChamber(enum.Enum):
    SENATE = 1
    ASSEMBLY = 2


class Bill(db.Model):
    """
    Base table for all bills, both city and state. Contains any info that's
    relevant for both kinds of bills.

    Bills are polymorphic. This table has a "type" which specifies whether it's
    a city or a state bill, and there will be an associated row in the CityBill
    and StateBill with more info on it."""

    __tablename__ = "bills"

    class BillType(enum.Enum):
        CITY = 1
        STATE = 2

    id = Column(UUID, primary_key=True, default=uuid4)

    # For city this is the "MatterName", for state it is the "title"
    name = Column(Text, nullable=False)

    # For city this is the "title", for state this is the "summary"
    description = Column(Text, nullable=False)

    # Info on child objects:
    type = Column(Enum(BillType), nullable=False)

    # If this is is a city bill, points to more specific data on that.
    city_bill = relationship(
        "CityBill",
        back_populates="bill",
        uselist=False,
        cascade="all, delete",
        lazy="joined",
    )

    # If this is is a state bill, points to more specific data on that.
    state_bill = relationship(
        "StateBill",
        back_populates="bill",
        uselist=False,
        cascade="all, delete",
        lazy="joined",
    )

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

    @property
    def tracked(self):
        return True

    @property
    def status(self):
        if self.type == Bill.BillType.CITY:
            return self.city_bill.status

        senate_status = (
            self.state_bill.senate_bill.status
            if self.state_bill.senate_bill
            else "(No Senate bill)"
        )
        assembly_status = (
            self.state_bill.assembly_bill.status
            if self.state_bill.assembly_bill
            else "(No Assembly bill)"
        )

        return f"{senate_status} / {assembly_status}"

    @property
    def code_name(self):
        if self.type == Bill.BillType.CITY:
            return self.city_bill.file

        senate_print_no = (
            self.state_bill.senate_bill.base_print_no
            if self.state_bill.senate_bill
            else "(No Senate bill)"
        )
        assembly_print_no = (
            self.state_bill.assembly_bill.base_print_no
            if self.state_bill.assembly_bill
            else "(No Assembly bill)"
        )

        return f"{senate_print_no} / {assembly_print_no} from {self.state_bill.session_year} session"
    
    user_bill_settings = relationship("UserBillSettings", back_populates="bill", cascade="all, delete-orphan")


class BillAttachment(db.Model):
    __tablename__ = "bill_attachments"

    id = Column(UUID, primary_key=True, default=uuid4)
    bill_id = Column(UUID, ForeignKey("bills.id"), nullable=False, index=True)
    bill = relationship("Bill", back_populates="attachments")

    name = Column(Text)
    url = Column(Text, nullable=False)


class PowerHour(db.Model):
    __tablename__ = "power_hours"

    id = Column(UUID, primary_key=True, default=uuid4)
    bill_id = Column(UUID, ForeignKey("bills.id"), nullable=False, index=True)

    title = Column(Text)
    spreadsheet_url = Column(Text, nullable=False)
    spreadsheet_id = Column(Text, nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, default=now)
    bill = relationship("Bill", back_populates="power_hours")


class CityBill(db.Model):
    """
    City-specific details about an NYC bill. There must also be an associated
    row in the Bill parent table that has more general bill info (like name).
    """

    __tablename__ = "city_bills"

    bill_id = Column(UUID, ForeignKey(Bill.id), primary_key=True)

    # ID in the City Council API
    city_bill_id = Column(Integer, nullable=False, unique=True, index=True)

    # Code name often used to discuss the bill, like Int 2317-2021
    file = Column(Text, nullable=False)

    # The parent Bill object that represents this.
    bill = relationship("Bill", back_populates="city_bill", lazy="joined")

    intro_date = Column(TIMESTAMP, nullable=False)

    status = Column(Text, nullable=False)

    # Which amendment version is currently active. We only track one at a time,
    # and sponsorships are tied to that particular version.
    active_version = Column(Text, nullable=False)

    sponsorships = relationship(
        "CitySponsorship", back_populates="city_bill", cascade="all, delete"
    )

    # Committee name
    council_body = Column(Text)


# TODO: Understand bill substitution and change if needed
class StateBill(db.Model):
    """
    State-specific details about a state bill. There must also be an associated
    row in the Bill parent table that has more general bill info (like name)."""

    __tablename__ = "state_bills"

    bill_id = Column(UUID, ForeignKey(Bill.id), primary_key=True)
    bill = relationship(Bill, back_populates="state_bill", lazy="joined")

    # The start of the 2-year legislative session this belongs to.
    session_year = Column(Integer, nullable=False)

    senate_bill = relationship(
        "SenateBill",
        back_populates="state_bill",
        uselist=False,
        cascade="all, delete",
    )
    assembly_bill = relationship(
        "AssemblyBill",
        back_populates="state_bill",
        uselist=False,
        cascade="all, delete",
    )


class StateChamberMixin:
    """
    Mixin for a bill in either the Senate or Assembly chamber. The have
    identical structure but are kept in separate tables."""

    active_version = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    base_print_no = Column(Text, nullable=False)

    @declared_attr
    def bill_id(self):
        return Column(UUID, ForeignKey(StateBill.bill_id), primary_key=True)

    # The Senate and the Assembly each run separate websites, and each website can
    # lookup both senate and assembly bills. So they're redundant websites with
    # very different UI. Therefore senate and assembly bills each have a
    # both assembly and senate websites.
    @property
    def senate_website(self):
        return f"https://www.nysenate.gov/legislation/bills/{self.state_bill.session_year}/{self.base_print_no}"

    @property
    def assembly_website(self):
        return f"https://nyassembly.gov/leg/?term={self.state_bill.session_year}&bn={self.base_print_no}"


class SenateBill(db.Model, StateChamberMixin):
    __tablename__ = "senate_bills"

    state_bill = relationship(StateBill, back_populates="senate_bill")
    sponsorships = relationship(
        "SenateSponsorship",
        back_populates="chamber_bill",
        cascade="all, delete-orphan",
    )


class AssemblyBill(db.Model, StateChamberMixin):
    __tablename__ = "assembly_bills"

    state_bill = relationship(StateBill, back_populates="assembly_bill")
    sponsorships = relationship(
        "AssemblySponsorship",
        back_populates="chamber_bill",
        cascade="all, delete-orphan",
    )


class UserBillSettings(db.Model):
    __tablename__ = "user_bill_settings"

    bill_id = Column(UUID, ForeignKey(Bill.id), primary_key=True)
    user_id = Column(UUID, ForeignKey(User.id), primary_key=True)

    send_bill_update_notifications = Column(
        Boolean, nullable=False, server_default=sql.false()
    )

    user = relationship(User, lazy="joined", back_populates="bill_settings")
    bill = relationship(Bill, back_populates="user_bill_settings")


Bill.viewer_settings = relationship(
    UserBillSettings,
    primaryjoin=(remote(UserBillSettings.bill_id) == foreign(Bill.id))
    & (
        UserBillSettings.user_id
        == sql.bindparam(
            "request_user_id", callable_=lambda: flask.g.request_user_id
        )
    ),
    viewonly=True,
)
