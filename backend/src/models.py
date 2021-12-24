from uuid import uuid4

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Text,
    TypeDecorator,
    sql,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import TIMESTAMP as _TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as _UUID
from sqlalchemy.orm import relationship

from .app import app
from .utils import now

db = SQLAlchemy(app)


class UUID(TypeDecorator):
    impl = _UUID(as_uuid=True)


class TIMESTAMP(TypeDecorator):
    impl = _TIMESTAMP(timezone=True)


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


class PowerHour(db.Model):
    __tablename__ = "power_hours"

    id = Column(UUID, primary_key=True, default=uuid4)
    bill_id = Column(
        Integer, ForeignKey("bills.id"), nullable=False, index=True
    )

    title = Column(Text)
    spreadsheet_url = Column(Text, nullable=False)
    spreadsheet_id = Column(Text, nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, default=now)
    bill = relationship("Bill", back_populates="power_hours")


class User(db.Model):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, default=uuid4)

    email = Column(
        Text, index=True, nullable=False, unique=True
    )  # always lowercase
    name = Column(Text)

    login_links = relationship(
        "LoginLink", back_populates="user", cascade="all, delete"
    )

    # The "root" user can never be deleted.
    can_be_deleted = Column(Boolean, nullable=False, server_default=sql.true())

    send_bill_update_notifications = Column(
        Boolean, nullable=False, server_default=sql.false(), index=True
    )

    __table_args__ = (
        CheckConstraint(
            "email = lower(email)", name="check_email_is_lowercase"
        ),
    )


class LoginLink(db.Model):
    __tablename__ = "login_links"

    user_id = Column(UUID, ForeignKey(User.id), nullable=False)

    token = Column(Text, nullable=False, primary_key=True)

    expires_at = Column(TIMESTAMP, nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, default=now)

    user = relationship("User", back_populates="login_links")

    # TODO: Consider only allowing these links to be used once. Better security
    # in case of leaked browser URL, but worse UX.
