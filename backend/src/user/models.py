from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Text, sql
from sqlalchemy.orm import relationship

from ..models import TIMESTAMP, UUID, db
from ..utils import now


class User(db.Model):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, default=uuid4)

    email = Column(
        Text, index=True, nullable=False, unique=True
    )  # always lowercase
    name = Column(Text)

    login_links = relationship(
        "LoginLink", back_populates="user", cascade="all, delete-orphan"
    )

    # The "root" user can never be deleted.
    can_be_deleted = Column(Boolean, nullable=False, server_default=sql.true())

    bill_settings = relationship(
        "UserBillSettings", back_populates="user", cascade="all, delete-orphan"
    )

    bills_with_notifications = relationship(
        "Bill",
        secondary="user_bill_settings",
        primaryjoin="and_(UserBillSettings.user_id==User.id, UserBillSettings.send_bill_update_notifications)",
        secondaryjoin="UserBillSettings.bill_id==Bill.id",
        viewonly=True,
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

    used_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="login_links")

    # TODO: Consider only allowing these links to be used once. Better security
    # in case of leaked browser URL, but worse UX.


# TODO: Make these linkes only usably once
# We would need to have a good error page for this too, if they click it a second time
