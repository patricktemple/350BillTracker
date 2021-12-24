import logging
from datetime import date, timedelta
from uuid import uuid4

import flask
from flask import jsonify, render_template, request
from marshmallow import fields
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, relationship
from werkzeug import exceptions

from ..app import app
from ..auth import auth_required, create_jwt
from ..council_api import lookup_bill, lookup_bills
from ..council_sync import update_bill_sponsorships
from ..models import db
from ..utils import now
from ..views import CamelCaseSchema
from .models import Bill
from .schema import BillSchema

# Views ----------------------------------------------------------------------


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
