from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text, TypeDecorator, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP as _TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as _UUID
from sqlalchemy import sql

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

    sponsorships = relationship("BillSponsorship", back_populates="bill")
    attachments = relationship("BillAttachment", back_populates="bill")


class Legislator(db.Model):
    __tablename__ = "legislators"

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


    # Our info
    notes = Column(Text)




class BillSponsorship(db.Model):
    __tablename__ = "bill_sponsorships"

    bill_id = Column(Integer, ForeignKey('bills.id'), nullable=False, primary_key=True)
    bill = relationship("Bill", back_populates="sponsorships")

    # TODO: What if they don't exist in the DB?
    legislator_id = Column(Integer, ForeignKey('legislators.id'), nullable=False, primary_key=True)
    legislator = relationship("Legislator", back_populates="sponsorships")


# TODO: UUIDs for some PKs?
class BillAttachment(db.Model):
    __tablename__ = "bill_attachments"

    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey('bills.id'), nullable=False, index=True)
    bill = relationship("Bill", back_populates="attachments")

    name = Column(Text)
    url = Column(Text, nullable=False)