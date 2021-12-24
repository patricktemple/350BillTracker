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
