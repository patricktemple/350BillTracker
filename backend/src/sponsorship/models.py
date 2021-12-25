from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..models import TIMESTAMP, db, UUID
from ..person.models import Senator, AssemblyMember, CouncilMember, Person
from ..bill.models import CityBill, SenateBillVersion, AssemblyBillVersion, Bill

class CitySponsorship(db.Model):
    __tablename__ = "city_sponsorships"

    bill_id = Column(
        UUID, ForeignKey("city_bills.bill_id"), nullable=False, primary_key=True
    )
    city_bill = relationship(
        CityBill, back_populates="sponsorships" # , order_by="Bill.name" # PROBLEM with this order by
    )
    bill = relationship(Bill, primaryjoin="Bill.id==CityBill.bill_id")

    council_member_id = Column(
        UUID, ForeignKey("council_members.person_id"), nullable=False, primary_key=True
    )
    council_member = relationship(
        CouncilMember, back_populates="sponsorships" # , order_by="CityCouncilMember.name" # ugh --- this should order by Person.name?
    )
    person = relationship(
        Person, primaryjoin="Person.id==CitySponsorship.council_member_id"
    )

    # TODO: Make this nullable=false once cron has run in prod and backfilled
    sponsor_sequence = Column(Integer, nullable=True)
    # The timestamp when we first saw this sponsorship in the bill's list.
    # This is a proxy for when the sponsor actually signed on to the bill.
    # Note that when we first start tracking a bill, it may already have sponsorships
    # and we don't know the date that those were added. We leave added_at as null,
    # in that case, and only fill this in for sponsorships that were added later on.
    added_at = Column(TIMESTAMP)


class SenateSponsorship(db.Model):
    __tablename__ = "senate_sponsorships"

    id = Column(UUID, primary_key=True)

    senate_version_id = Column(
        UUID, ForeignKey(SenateBillVersion.id), nullable=False
    )
    senate_version = relationship(
        SenateBillVersion, back_populates="sponsorships"# , order_by="Bill.name"
    )

    senator_id = Column(
        UUID, ForeignKey(Senator.person_id), nullable=False
    )
    senator = relationship(
        Senator, back_populates="sponsorships" #
    )

    # # TODO: Make this nullable=false once cron has run in prod and backfilled
    # sponsor_sequence = Column(Integer, nullable=True)

    # # The timestamp when we first saw this sponsorship in the bill's list.
    # # This is a proxy for when the sponsor actually signed on to the bill.
    # # Note that when we first start tracking a bill, it may already have sponsorships
    # # and we don't know the date that those were added. We leave added_at as null,
    # # in that case, and only fill this in for sponsorships that were added later on.
    # added_at = Column(TIMESTAMP)


class AssemblySponsorship(db.Model):
    __tablename__ = "assembly_sponsorships"

    id = Column(UUID, primary_key=True)

    assembly_version_id = Column(
        UUID, ForeignKey(AssemblyBillVersion.id), nullable=False
    )
    assembly_version = relationship(
        AssemblyBillVersion, back_populates="sponsorships"# , order_by="Bill.name"
    )

    assembly_member_id = Column(
        UUID, ForeignKey(AssemblyMember.person_id), nullable=False
    )
    assembly_member = relationship(
        AssemblyMember, back_populates="sponsorships" #
    )

    # # TODO: Make this nullable=false once cron has run in prod and backfilled
    # sponsor_sequence = Column(Integer, nullable=True)

    # # The timestamp when we first saw this sponsorship in the bill's list.
    # # This is a proxy for when the sponsor actually signed on to the bill.
    # # Note that when we first start tracking a bill, it may already have sponsorships
    # # and we don't know the date that those were added. We leave added_at as null,
    # # in that case, and only fill this in for sponsorships that were added later on.
    # added_at = Column(TIMESTAMP)