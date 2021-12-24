from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..models import TIMESTAMP, db


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
    # TODO: Make this nullable=false once cron has run in prod and backfilled
    sponsor_sequence = Column(Integer, nullable=True)

    # The timestamp when we first saw this sponsorship in the bill's list.
    # This is a proxy for when the sponsor actually signed on to the bill.
    # Note that when we first start tracking a bill, it may already have sponsorships
    # and we don't know the date that those were added. We leave added_at as null,
    # in that case, and only fill this in for sponsorships that were added later on.
    added_at = Column(TIMESTAMP)
