from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from ..models import TIMESTAMP, UUID, db


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
    staffers = relationship("Staffer", back_populates="legislator")

    borough = Column(Text)
    website = Column(Text)

    # These are added by our static data
    twitter = Column(Text)  # exclude the @ symbol
    party = Column(Text)

    # Track our own info on the bill.
    notes = Column(Text)

    @property
    def display_twitter(self):
        return "@" + self.twitter if self.twitter else None

    @property
    def twitter_url(self):
        return (
            f"https://www.twitter.com/{self.twitter}" if self.twitter else None
        )


class Staffer(db.Model):
    __tablename__ = "staffers"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(Text, nullable=False)
    title = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    legislator_id = Column(
        Integer, ForeignKey("legislators.id"), nullable=False
    )
    twitter = Column(Text)

    legislator = relationship("Legislator", back_populates="staffers")

    @property
    def display_twitter(self):
        return "@" + self.twitter if self.twitter else None

    @property
    def display_string(self):
        contact_methods = [self.phone, self.email, self.display_twitter]
        contact_methods = [c for c in contact_methods if c]
        contact_string = ", ".join(contact_methods)
        if not contact_string:
            contact_string = "No contact info"
        title_string = f"{self.title} - " if self.title else ""

        return f"{title_string}{self.name} ({contact_string})"
