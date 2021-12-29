import enum
from uuid import uuid4

from sqlalchemy import Column, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import column_property, relationship
from sqlalchemy import func, select

from ..models import TIMESTAMP, UUID, db
from ..utils import now

DEFAULT_TWITTER_SEARCH_TERMS = [
    "solar",
    "climate",
    "wind power",
    "renewable",
    "fossil fuel",
]



# Let's standardize some fields across city and state:
# Bill.name is shorter, maps to city council's MatterName and State's "title"
# Bill.description is longer, maps to city council's "title" and state's "summary"
# Code_name is a derived property. Comes from CityBill.file, or a combo of state bill's two code names
# Should we do the same with status?
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

        senate_status = self.state_bill.senate_bill.status if self.state_bill.senate_bill else "(No Senate bill)"
        assembly_status = self.state_bill.assembly_bill.status if self.state_bill.assembly_bill else "(No Assembly bill)"
    
        # This seems wrong... figure out how substitutions work
        return f"{senate_status} / {assembly_status}"
    
    @property
    def code_name(self):
        if self.type == Bill.BillType.CITY:
            return self.city_bill.file

        senate_print_no = self.state_bill.senate_bill.base_print_no if self.state_bill.senate_bill else "(No Senate bill)"
        assembly_print_no = self.state_bill.assembly_bill.base_print_no if self.state_bill.assembly_bill else "(No Assembly bill)"
    
        # This seems wrong... figure out how substitutions work
        return f"{senate_print_no} / {assembly_print_no}"


class BillAttachment(db.Model):
    __tablename__ = "bill_attachments"

    id = Column(UUID, primary_key=True, default=uuid4)
    bill_id = Column(
        UUID, ForeignKey("bills.id"), nullable=False, index=True
    )
    bill = relationship("Bill", back_populates="attachments")

    name = Column(Text)
    url = Column(Text, nullable=False)


class PowerHour(db.Model):
    __tablename__ = "power_hours"

    id = Column(UUID, primary_key=True, default=uuid4)
    bill_id = Column(
        UUID, ForeignKey("bills.id"), nullable=False, index=True
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


# TODO: Understand bill substitution, I have something wrong here... seems like after passing one chamber, it gets substituted for the other one? unclear...
class StateBill(db.Model):
    """
    State-specific details about a state bill. There must also be an associated
    row in the Bill parent table that has more general bill info (like name)."""

    __tablename__ = "state_bills"

    bill_id = Column(UUID, ForeignKey(Bill.id), primary_key=True)
    bill = relationship(Bill, back_populates="state_bill", lazy="joined")

    # The start of the 2-year legislative session this belongs to.
    session_year = Column(Integer, nullable=False)

    # Is this right? Or should it be on state chamber mixin?
    # Is this a FK to SenateBillVersion?
    # active_senate_version = Column(Text, nullable=False, default="")
    # active_assembly_version = Column(Text, nullable=False, default="")

    # make a relationship to active version

    senate_bill = relationship("SenateBill", back_populates="state_bill", uselist=False)
    assembly_bill = relationship("AssemblyBill", back_populates="state_bill", uselist=False)

    # Foreign key options to the version
    # 2021/S04251/A --> not great, it's a triple foreign key and the other two are not the real ID
    # bill_id/A --> this works, as long as SenateBillVersion is a separate table from AssemblyBillVersion
    # just have a foreign key to the active version: this could work, though you need a transaction to keep the two in sync. you end up with double foreign keys pointing vice-versa.
    # only keep the "active" version around at all in a table. this is simplest!! and it keeps other things cleaner... let's do this unless we don't need to do otherwise


class StateChamberMixin:
    id = Column(UUID, primary_key=True, default=uuid4) # unclear that this ID column is necessary if we have just one version at a time
 
    active_version_name = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    base_print_no = Column(Text, nullable=False)

    @property
    def sponsor_count(self):
        # TODO: Implement
        return 0

    @declared_attr
    def bill_id(self):
       return Column(UUID, ForeignKey(StateBill.bill_id), index=True) # todo make this unique (same below)

    # This is a bit confusing. The Senate and the Assembly each run separate websites,
    # and each website can lookup both senate and assembly bills. So they're redundant
    # websites with very different UI. Therefore senate and assembly bills each have a
    # both assembly and senate websites.
    @property
    def senate_website_url(self):
        return f"https://www.nysenate.gov/legislation/bills/{self.state_bill.session_year}/{self.base_print_no}"
    
    @property
    def assembly_website_url(self):
        # use urlpasr to construct it?
        return f"https://nyassembly.gov/leg/?term={self.state_bill.session_year}&bn={self.base_print_no}"

# todo comment about versions and stuff
class SenateBill(db.Model, StateChamberMixin):
    __tablename__ = "senate_bills"

    state_bill = relationship(StateBill, back_populates="senate_bill")
    sponsorships = relationship(
        "SenateSponsorship", back_populates="senate_version"
    )


class AssemblyBill(db.Model, StateChamberMixin):
    __tablename__ = "assembly_bills"

    state_bill = relationship(StateBill, back_populates="assembly_bill")
    sponsorships = relationship(
        "AssemblySponsorship", back_populates="assembly_version"
    )
