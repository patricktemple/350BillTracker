from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..models import TIMESTAMP, db

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