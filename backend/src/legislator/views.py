import logging
import re
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
from .models import Legislator, Staffer
from .schema import LegislatorSchema, StafferSchema


@app.route("/api/legislators", methods=["GET"])
@auth_required
def get_legislators():
    legislators = Legislator.query.order_by(Legislator.name).all()
    return LegislatorSchema(many=True).jsonify(legislators)


@app.route("/api/legislators/<int:legislator_id>", methods=["PUT"])
@auth_required
def update_legislator(legislator_id):
    data = LegislatorSchema().load(request.json)

    legislator = Legislator.query.get(legislator_id)
    legislator.notes = data["notes"]

    db.session.commit()

    return jsonify({})


@app.route("/api/legislators/<int:legislator_id>/staffers", methods=["GET"])
@auth_required
def legislator_staffers(legislator_id):
    staffers = Staffer.query.filter_by(legislator_id=legislator_id).all()
    return StafferSchema(many=True).jsonify(staffers)


@app.route("/api/legislators/<int:legislator_id>/staffers", methods=["POST"])
@auth_required
def add_legislator_staffer(legislator_id):
    data = StafferSchema().load(request.json)
    twitter = data["twitter"]
    if twitter:
        if twitter.startswith("@"):
            twitter = twitter[1:]
        pattern = re.compile("^[A-Za-z0-9_]{1,15}$")
        if not pattern.match(twitter):
            raise exceptions.UnprocessableEntity(f"Invalid Twitter: {twitter}")

    staffer = Staffer(
        legislator_id=legislator_id,
        name=data["name"],
        title=data["title"],
        phone=data["phone"],
        email=data["email"],
        twitter=twitter,
    )
    db.session.add(staffer)
    db.session.commit()

    # TODO: Return the object in all Creates, to be consistent
    return jsonify({})


@app.route("/api/legislators/-/staffers/<uuid:staffer_id>", methods=["DELETE"])
@auth_required
def delete_staffer(staffer_id):
    staffer = Staffer.query.get(staffer_id)
    if not staffer:
        raise exceptions.NotFound()
    db.session.delete(staffer)
    db.session.commit()

    # TODO: Return the object in all Creates, to be consistent
    return jsonify({})
