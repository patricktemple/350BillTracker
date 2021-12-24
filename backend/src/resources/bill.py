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
from sqlalchemy.orm import relationship
from ..auth import auth_required, create_jwt


from ..council_api import lookup_bill, lookup_bills
from ..utils import now
from ..models import db, TIMESTAMP, UUID
from ..views import CamelCaseSchema
from marshmallow import fields

import logging
import re
import secrets
from datetime import date, timedelta

import flask
from flask import jsonify, render_template, request
from marshmallow import fields
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from werkzeug import exceptions

from ..app import app


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


class BillSchema(CamelCaseSchema):
    # Data pulled from the API
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    title = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    body = fields.String(dump_only=True)
    file = fields.String(dump_only=True)

    # Data that we track
    tracked = fields.Boolean(dump_only=True)
    notes = fields.String(required=True)
    nickname = fields.String(required=True)
    twitter_search_terms = fields.List(fields.String(), required=True)


# Views ----------------------------------------------------------------------
from ..council_sync import update_bill_sponsorships


@app.route("/api/saved-bills", methods=["GET"])
@auth_required
def bills():
    bills = Bill.query.order_by(Bill.name).all()
    return BillSchema(many=True).jsonify(bills)


@app.route("/api/saved-bills", methods=["POST"])
@auth_required
def save_bill():
    bill_id = request.json["id"]
    if Bill.query.get(bill_id):
        # There's a race condition of checking this and then inserting,
        # but in that rare case it will hit the DB unique constraint instead.
        raise exceptions.Conflict()

    bill_data = lookup_bill(bill_id)
    logging.info(f"Saving bill {bill_id}, council API returned {bill_data}")

    bill = Bill(**bill_data)
    db.session.add(bill)

    update_bill_sponsorships(bill_id)

    db.session.commit()

    return jsonify({})


@app.route("/api/saved-bills/<int:bill_id>", methods=["PUT"])
@auth_required
def update_bill(bill_id):
    data = BillSchema().load(request.json)

    bill = Bill.query.get(bill_id)
    bill.notes = data["notes"]
    bill.nickname = data["nickname"]

    bill.twitter_search_terms = data["twitter_search_terms"]

    db.session.commit()

    return jsonify({})


@app.route("/api/saved-bills/<int:bill_id>", methods=["DELETE"])
@auth_required
def delete_bill(bill_id):
    bill = Bill.query.get(bill_id)
    db.session.delete(bill)
    db.session.commit()

    return jsonify({})


@app.route("/api/search-bills", methods=["GET"])
@auth_required
def search_bills():
    file = request.args.get("file")

    external_bills = lookup_bills(file)

    # Check whether or not we're already tracking this bill
    external_bills_ids = [b["id"] for b in external_bills]
    tracked_bills = Bill.query.filter(Bill.id.in_(external_bills_ids)).all()
    tracked_bill_ids = set([t.id for t in tracked_bills])

    for bill in external_bills:
        bill["tracked"] = bill["id"] in tracked_bill_ids

    return BillSchema(many=True).jsonify(external_bills)