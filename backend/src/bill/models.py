import enum
from uuid import uuid4

from sqlalchemy import Column, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from ..app import app
from ..models import TIMESTAMP, UUID, db
from ..utils import now

DEFAULT_TWITTER_SEARCH_TERMS = [
    "solar",
    "climate",
    "wind power",
    "renewable",
    "fossil fuel",
]


class Bill(db.Model):
    """
    Base table for all bills, both city and state. Contains any info that's
    relevant for both kinds of bills.

    Bills are polymorphic. This table has a "type" which specifies whether it's
    a city or a state bill, and there will be an associated row in the CityBill
    and StateBill with more info on it."""

    # TODO: Fix these table names:
    __tablename__ = "bills_2"

    class BillType(enum.Enum):
        CITY = 1
        STATE = 2

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(Text, nullable=False)

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


class BillAttachment(db.Model):
    __tablename__ = "bill_attachments_2"

    id = Column(UUID, primary_key=True, default=uuid4)
    bill_id = Column(
        UUID, ForeignKey("bills_2.id"), nullable=False, index=True
    )
    bill = relationship("Bill", back_populates="attachments")

    name = Column(Text)
    url = Column(Text, nullable=False)


class PowerHour(db.Model):
    __tablename__ = "power_hours_2"

    id = Column(UUID, primary_key=True, default=uuid4)
    bill_id = Column(
        UUID, ForeignKey("bills_2.id"), nullable=False, index=True
    )

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

    title = Column(Text, nullable=False)

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


class StateBill(db.Model):
    """
    State-specific details about a state bill. There must also be an associated
    row in the Bill parent table that has more general bill info (like name)."""

    __tablename__ = "state_bills"

    bill_id = Column(UUID, ForeignKey(Bill.id), primary_key=True)
    bill = relationship(Bill, back_populates="state_bill", lazy="joined")


class SenateBillVersion(db.Model):
    __tablename__ = "senate_bill_versions"

    id = Column(UUID, primary_key=True)
    bill_id = Column(UUID, ForeignKey(StateBill.bill_id), index=True)
    version_name = Column(Text, nullable=False)
    sponsorships = relationship(
        "SenateSponsorship", back_populates="senate_version"
    )


class AssemblyBillVersion(db.Model):
    __tablename__ = "assembly_bill_versions"

    id = Column(UUID, primary_key=True)
    bill_id = Column(UUID, ForeignKey(StateBill.bill_id), index=True)
    version_name = Column(Text, nullable=False)
    sponsorships = relationship(
        "AssemblySponsorship", back_populates="assembly_version"
    )
