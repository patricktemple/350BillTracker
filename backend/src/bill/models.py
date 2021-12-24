from uuid import uuid4

import flask
from flask import jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from sqlalchemy import Column, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, relationship
from werkzeug import exceptions

from ..app import app
from ..models import TIMESTAMP, UUID, db
from ..utils import now

# Model -----------------------------------------------------------------------

DEFAULT_TWITTER_SEARCH_TERMS = [
    "solar",
    "climate",
    "wind power",
    "renewable",
    "fossil fuel",
]


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

    twitter_search_terms = Column(
        ARRAY(Text), nullable=False, default=DEFAULT_TWITTER_SEARCH_TERMS
    )

    sponsorships = relationship(
        "BillSponsorship", back_populates="bill", cascade="all, delete"
    )
    attachments = relationship(
        "BillAttachment", back_populates="bill", cascade="all, delete"
    )
    power_hours = relationship(
        "PowerHour", back_populates="bill", cascade="all, delete"
    )

    @property
    def display_name(self):
        return self.nickname if self.nickname else self.name
