from datetime import date

from flask import jsonify, render_template, request
from marshmallow import fields
from sqlalchemy.orm import joinedload

from .app import app
from .app import marshmallow as ma
from .council_api import lookup_bills
from .council_sync import (
    add_or_update_bill,
    convert_matter_to_bill,
    update_sponsorships,
)
from .google_sheets import create_phone_bank_spreadsheet
from .models import Bill, BillAttachment, BillSponsorship, Legislator, db, User, LoginLink
from .utils import now
from datetime import timedelta
import secrets


def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


class CamelCaseSchema(ma.Schema):
    """Schema that uses camel-case for its external representation
    and snake-case for its internal representation.
    """

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


@app.route("/healthz", methods=["GET"])
def healthz():
    return "Healthy!"


# TODO: Hitting a react route other than root will fail when browser navigates directly there
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    return render_template("index.html")


# Bills ----------------------------------------------------------------------


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


@app.route("/api/saved-bills", methods=["GET"])
def bills():
    bills = Bill.query.order_by(Bill.name).all()
    return BillSchema(many=True).jsonify(bills)


@app.route("/api/saved-bills", methods=["POST"])
def save_bill():
    matter_id = request.json["id"]
    add_or_update_bill(matter_id)
    update_sponsorships(matter_id)

    return jsonify({})


@app.route("/api/saved-bills/<int:bill_id>", methods=["PUT"])
def update_bill(bill_id):
    data = BillSchema().load(request.json)

    bill = Bill.query.get(bill_id)
    bill.notes = data["notes"]
    bill.nickname = data["nickname"]

    db.session.commit()

    return jsonify({})


@app.route("/api/saved-bills/<int:bill_id>", methods=["DELETE"])
def delete_bill(bill_id):
    bill = Bill.query.get(bill_id)
    db.session.delete(bill)
    db.session.commit()

    return jsonify({})


@app.route("/api/search-bills", methods=["GET"])
def search_bills():
    file = request.args.get("file")

    matters = lookup_bills(file)

    # Check whether or not we're already tracking this bill
    external_bills = [convert_matter_to_bill(m) for m in matters]
    external_bills_ids = [b["id"] for b in external_bills]
    tracked_bills = Bill.query.filter(Bill.id.in_(external_bills_ids)).all()
    tracked_bill_ids = set([t.id for t in tracked_bills])

    for bill in external_bills:
        bill["tracked"] = bill["id"] in tracked_bill_ids

    return BillSchema(many=True).jsonify(external_bills)


# Legislators ----------------------------------------------------------------------


class LegislatorSchema(CamelCaseSchema):
    # Data synced from the API
    name = fields.String(dump_only=True)
    id = fields.Integer(dump_only=True)
    term_start = fields.DateTime(dump_only=True)
    term_end = fields.DateTime(dump_only=True)
    email = fields.String(dump_only=True)
    district_phone = fields.String(dump_only=True)
    legislative_phone = fields.String(dump_only=True)
    borough = fields.String(dump_only=True)
    website = fields.String(dump_only=True)

    # Static data that we add in
    twitter = fields.String(dump_only=True)

    # TODO: Make this an enum!
    party = fields.String(dump_only=True)

    # Extra data we track
    notes = fields.String(missing=None)


class SingleMemberSponsorshipsSchema(CamelCaseSchema):
    legislator_id = fields.Integer(required=True)
    bill = fields.Nested(BillSchema)


@app.route("/api/legislators", methods=["GET"])
def get_legislators():
    legislators = Legislator.query.order_by(Legislator.name).all()
    return LegislatorSchema(many=True).jsonify(legislators)


@app.route("/api/legislators/<int:legislator_id>", methods=["PUT"])
def update_legislator(legislator_id):
    data = LegislatorSchema().load(request.json)

    legislator = Legislator.query.get(legislator_id)
    legislator.notes = data["notes"]

    db.session.commit()

    return jsonify({})


@app.route(
    "/api/legislators/<int:legislator_id>/sponsorships", methods=["GET"]
)
def legislator_sponsorships(legislator_id):
    # TODO: No need to wrap this object, just return the list of sponsor people?
    sponsorships = (
        BillSponsorship.query.filter_by(legislator_id=legislator_id)
        .options(joinedload(BillSponsorship.bill))
        .all()
    )
    return SingleMemberSponsorshipsSchema(many=True).jsonify(sponsorships)


# Bill sponsorships ----------------------------------------------------------------------
class SingleBillSponsorshipsSchema(CamelCaseSchema):
    bill_id = fields.Integer(required=True)
    legislator = fields.Nested(LegislatorSchema)


@app.route("/api/saved-bills/<int:bill_id>/sponsorships", methods=["GET"])
def bill_sponsorships(bill_id):
    # TODO: No need to wrap this object, just return the list of sponsor people?
    sponsorships = (
        BillSponsorship.query.filter_by(bill_id=bill_id)
        .options(joinedload(BillSponsorship.legislator))
        .all()
    )
    return SingleBillSponsorshipsSchema(many=True).jsonify(sponsorships)


# Bill attachments ----------------------------------------------------------------------
class BillAttachmentSchema(CamelCaseSchema):
    id = fields.Integer()
    bill_id = fields.Integer()
    name = fields.String()
    url = fields.String()


@app.route("/api/saved-bills/<int:bill_id>/attachments", methods=["GET"])
def bill_attachments(bill_id):
    attachments = BillAttachment.query.filter_by(bill_id=bill_id).all()
    return BillAttachmentSchema(many=True).jsonify(attachments)


@app.route("/api/saved-bills/<int:bill_id>/attachments", methods=["POST"])
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
def delete_bill_attachment(attachment_id):
    attachment = BillAttachment.query.filter_by(id=attachment_id).one()
    db.session.delete(attachment)
    db.session.commit()

    return jsonify({})


@app.route(
    "/api/saved-bills/<int:bill_id>/create-phone-bank-spreadsheet",
    methods=["POST"],
)
def create_spreadsheet(bill_id):
    spreadsheet = create_phone_bank_spreadsheet(bill_id)
    attachment = BillAttachment(
        bill_id=bill_id,
        url=spreadsheet["spreadsheetUrl"],
        name=f"Power Hour Tracker (created {date.today().isoformat()})",
    )
    db.session.add(attachment)
    db.session.commit()
    return BillAttachmentSchema().jsonify(attachment)


# Login ----------------------------------------------------------------------
class CreateLoginLinkSchema(CamelCaseSchema):
    email = fields.String()


@app.route(
    "/api/create-login-link",
    methods=["POST"],
)
def create_login_link():
    data = CreateLoginLinkSchema().load(request.json)

    # TODO: Figure out lowercase stuff
    email_lower = data['email'].lower()
    user = User.query.filter_by(email=email_lower).one_or_none()
    if not user:
        # return API response instead
        raise ValueError("user not found")
    
    login = LoginLink(user_id=user.id, expires_at=now() + timedelta(days=1),
        token=secrets.token_urlsafe())
    db.session.add(login)
    db.session.commit()

    return jsonify({})

class LoginSchema(CamelCaseSchema):
    token = fields.String()


@app.route(
    "/api/login",
    methods=["POST"],
)
def login():
    data = LoginSchema().load(request.json)
    token = data['token']

    # TODO: Implement!
    return jsonify({
        "authToken": "This is a real token"
    })



# BUG: This seems to leave open stale SQLA sessions
