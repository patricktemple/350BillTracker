from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import TIMESTAMP as _TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as _UUID
from sqlalchemy.orm import relationship

from .app import app

db = SQLAlchemy(app)


class UUID(TypeDecorator):
    impl = _UUID(as_uuid=True)


class TIMESTAMP(TypeDecorator):
    impl = _TIMESTAMP(timezone=True)


class Bill(db.Model):
    __tablename__ = "bills"

    # These are all auto-populated by the API:
    id = Column(Integer, primary_key=True)
    file = Column(Text, nullable=False)  # e.g. Int 2317-2021
    name = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    status = Column(Text)
    body = Column(Text)

    intro_date = Column(TIMESTAMP, nullable=False)

    @property
    def tracked(self):
        return True

    # Data we track
    notes = Column(Text, nullable=False, server_default="")
    nickname = Column(Text, nullable=False, server_default="")

    sponsorships = relationship(
        "BillSponsorship", back_populates="bill", cascade="all, delete"
    )
    attachments = relationship(
        "BillAttachment", back_populates="bill", cascade="all, delete"
    )


# import enum
# from sqlalchemy import Integer, Enum

# class Party(enum.Enum):
#     DEMOCRATIC = 1
#     REPUBLICAN = 2


class Legislator(db.Model):
    __tablename__ = "legislators"

    # These come from the API
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    term_start = Column(TIMESTAMP)
    term_end = Column(TIMESTAMP)
    email = Column(Text)
    district_phone = Column(Text)
    legislative_phone = Column(Text)

    sponsorships = relationship("BillSponsorship", back_populates="legislator")

    borough = Column(Text)
    website = Column(Text)

    # These are added by our static data
    twitter = Column(Text)  # exclude the @ symbol
    party = Column(Text)

    # Track our own info on the bill.
    notes = Column(Text)


class BillSponsorship(db.Model):
    __tablename__ = "bill_sponsorships"

    bill_id = Column(
        Integer, ForeignKey("bills.id"), nullable=False, primary_key=True
    )
    bill = relationship(
        "Bill", back_populates="sponsorships", order_by="Bill.name"
    )

    legislator_id = Column(
        Integer, ForeignKey("legislators.id"), nullable=False, primary_key=True
    )
    legislator = relationship(
        "Legislator", back_populates="sponsorships", order_by="Legislator.name"
    )


# TODO: UUIDs for some PKs?
class BillAttachment(db.Model):
    __tablename__ = "bill_attachments"

    id = Column(Integer, primary_key=True)
    bill_id = Column(
        Integer, ForeignKey("bills.id"), nullable=False, index=True
    )
    bill = relationship("Bill", back_populates="attachments")

    name = Column(Text)
    url = Column(Text, nullable=False)
