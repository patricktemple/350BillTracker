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

from .app import app
from .app import marshmallow as ma
from .auth import auth_required, create_jwt
from .bill.models import Bill
from .bill.schema import BillSchema
from .google_sheets import create_power_hour
from .legislator.models import Legislator
from .legislator.schema import LegislatorSchema
from .models import BillAttachment, PowerHour, db
from .schema import CamelCaseSchema
from .ses import send_login_link_email
from .settings import APP_ORIGIN
from .twitter import get_bill_twitter_search_url
from .user.models import LoginLink, User
from .utils import now


@app.route("/healthz", methods=["GET"])
def healthz():
    return "Healthy!"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    return render_template("index.html")


# Bill attachments ----------------------------------------------------------------------
class BillAttachmentSchema(CamelCaseSchema):
    id = fields.Integer()
    bill_id = fields.Integer()
    name = fields.String()
    url = fields.String()


@app.route("/api/saved-bills/<int:bill_id>/attachments", methods=["GET"])
@auth_required
def bill_attachments(bill_id):
    attachments = BillAttachment.query.filter_by(bill_id=bill_id).all()
    return BillAttachmentSchema(many=True).jsonify(attachments)


@app.route("/api/saved-bills/<int:bill_id>/attachments", methods=["POST"])
@auth_required
def add_bill_attachment(bill_id):
    data = BillAttachmentSchema().load(request.json)
    attachment = BillAttachment(
        bill_id=bill_id,
        url=data["url"],
        name=data["name"],
    )
    db.session.add(attachment)
    db.session.commit()

    # TODO: Return the object in all Creates, to be consistent
    return jsonify({})


@app.route(
    "/api/saved-bills/-/attachments/<int:attachment_id>", methods=["DELETE"]
)
@auth_required
def delete_bill_attachment(attachment_id):
    attachment = BillAttachment.query.filter_by(id=attachment_id).one()
    db.session.delete(attachment)
    db.session.commit()

    return jsonify({})


class PowerHourSchema(CamelCaseSchema):
    id = fields.UUID(dump_only=True)
    power_hour_id_to_import = fields.UUID(load_only=True, missing=None)

    bill_id = fields.Integer(dump_only=True)
    title = fields.String()
    spreadsheet_url = fields.String(dump_only=True)
    created_at = fields.DateTime()


class CreatePowerHourSchema(CamelCaseSchema):
    power_hour = fields.Nested(PowerHourSchema)
    messages = fields.List(fields.String())


@app.route("/api/saved-bills/<int:bill_id>/power-hours", methods=["GET"])
@auth_required
def bill_power_hours(bill_id):
    power_hours = (
        PowerHour.query.filter_by(bill_id=bill_id)
        .order_by(PowerHour.created_at)
        .all()
    )
    return PowerHourSchema(many=True).jsonify(power_hours)


# TODO: Migrate existing power hours
@app.route(
    "/api/saved-bills/<int:bill_id>/power-hours",
    methods=["POST"],
)
@auth_required
def create_spreadsheet(bill_id):
    data = PowerHourSchema().load(request.json)
    power_hour_id_to_import = data.get("power_hour_id_to_import")
    if power_hour_id_to_import:
        power_hour = PowerHour.query.get(power_hour_id_to_import)
        old_spreadsheet_id = power_hour.spreadsheet_id
    else:
        old_spreadsheet_id = None

    spreadsheet, messages = create_power_hour(
        bill_id, data["title"], old_spreadsheet_id
    )

    power_hour = PowerHour(
        bill_id=bill_id,
        spreadsheet_url=spreadsheet["spreadsheetUrl"],
        spreadsheet_id=spreadsheet["spreadsheetId"],
        title=data["title"],
    )
    db.session.add(power_hour)
    db.session.commit()

    return CreatePowerHourSchema().jsonify(
        {"messages": messages, "power_hour": power_hour}
    )


# BUG: This seems to leave open stale SQLA sessions
