from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, Text, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
import enum

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
    type = Column(Enum(BillType), nullable=False)
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


# TODO: Figure out how to identify the active version
class SenateBillVersion(db.Model):
    __tablename__ = "senate_bill_versions"

    id = Column(UUID, primary_key=True)
    bill_id = Column(UUID, ForeignKey(StateBill.bill_id), index=True)
    version_name = Column(Text, nullable=False)


class AssemblyBillVersion(db.Model):
    # Use a base class for this and senate versions, maybe? and same for sponsorships
    __tablename__ = "assembly_bill_versions"

    id = Column(UUID, primary_key=True)
    bill_id = Column(UUID, ForeignKey(StateBill.bill_id), index=True)
    version_name = Column(Text, nullable=False)