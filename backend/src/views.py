import re
import secrets
from datetime import date, timedelta

from flask import jsonify, render_template, request
from marshmallow import fields
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from werkzeug import exceptions

from .app import app
from .app import marshmallow as ma
from .auth import auth_required, create_jwt
from .council_api import lookup_bills, lookup_bill
from .council_sync import (
    update_sponsorships,
)
from .google_sheets import create_phone_bank_spreadsheet
from .models import (
    Bill,
    BillAttachment,
    BillSponsorship,
    Legislator,
    LoginLink,
    Staffer,
    User,
    db,
)
from .ses import send_login_link_email
from .settings import APP_ORIGIN
from .utils import now
import logging


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
@auth_required
def bills():
    bills = Bill.query.order_by(Bill.name).all()
    return BillSchema(many=True).jsonify(bills)


@app.route("/api/saved-bills", methods=["POST"])
@auth_required
def save_bill():
    bill_id = request.json["id"]
    bill_data = lookup_bill(bill_id)
    logging.info(f"Saving bill {bill_id}, council API returned {bill_data}")

    bill = Bill(**bill_data)
    db.session.add(bill)

    # If we're already tracking this bill, this will have an integrity
    # error which is intentional.
    # TODO: Add test for this, return 409
    db.session.commit()

    # i think this is fine since we don't want to send notifications anyway?
    update_sponsorships(bill_id) # should this be in the same transaction?

    return jsonify({})


@app.route("/api/saved-bills/<int:bill_id>", methods=["PUT"])
@auth_required
def update_bill(bill_id):
    data = BillSchema().load(request.json)

    bill = Bill.query.get(bill_id)
    bill.notes = data["notes"]
    bill.nickname = data["nickname"]

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


@app.route(
    "/api/legislators/<int:legislator_id>/sponsorships", methods=["GET"]
)
@auth_required
def legislator_sponsorships(legislator_id):
    sponsorships = (
        BillSponsorship.query.filter_by(legislator_id=legislator_id)
        .options(joinedload(BillSponsorship.bill))
        .all()
    )
    return SingleMemberSponsorshipsSchema(many=True).jsonify(sponsorships)


# Staffers ----------------------------------------------------------------------


class StafferSchema(CamelCaseSchema):
    id = fields.UUID()
    name = fields.String()
    title = fields.String(missing=None)
    email = fields.Email(missing=None)
    phone = fields.String(missing=None)
    twitter = fields.String(missing=None)
    # TODO: Move twitter validation into schema


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


# Bill sponsorships ----------------------------------------------------------------------
class SingleBillSponsorshipsSchema(CamelCaseSchema):
    bill_id = fields.Integer(required=True)
    legislator = fields.Nested(LegislatorSchema)


@app.route("/api/saved-bills/<int:bill_id>/sponsorships", methods=["GET"])
@auth_required
def bill_sponsorships(bill_id):
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


@app.route(
    "/api/saved-bills/<int:bill_id>/create-phone-bank-spreadsheet",
    methods=["POST"],
)
@auth_required
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

    email_lower = data["email"].lower()
    user = User.query.filter_by(email=email_lower).one_or_none()
    if not user:
        raise exceptions.UnprocessableEntity("user not found")

    login = LoginLink(
        user_id=user.id,
        expires_at=now() + timedelta(days=1),
        token=secrets.token_urlsafe(),
    )
    db.session.add(login)
    db.session.commit()

    send_login_link_email(
        email_lower, f"{APP_ORIGIN}/login?token={login.token}"
    )

    return jsonify({})


class LoginSchema(CamelCaseSchema):
    token = fields.String()


@app.route(
    "/api/login",
    methods=["POST"],
)
def login():
    data = LoginSchema().load(request.json)
    token = data["token"]

    login_link = LoginLink.query.filter_by(token=token).one_or_none()
    if not login_link:
        raise exceptions.Unauthorized()

    user_id = login_link.user_id

    if login_link.expires_at < now():
        raise exceptions.Unauthorized()

    return jsonify({"authToken": create_jwt(user_id)})


# Users ----------------------------------------------------------------------
class UserSchema(CamelCaseSchema):
    id = fields.UUID()

    # TODO: On client side, handle email validation failure
    email = fields.Email()
    name = fields.String()
    can_be_deleted = fields.Boolean()


@app.route(
    "/api/users",
    methods=["GET"],
)
@auth_required
def list_users():
    users = User.query.all()

    return UserSchema(many=True).jsonify(users)


@app.route(
    "/api/users/<uuid:user_id>",
    methods=["DELETE"],
)
@auth_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user.can_be_deleted:
        raise exceptions.UnprocessableEntity()
    db.session.delete(user)
    db.session.commit()

    return jsonify({})


@app.route(
    "/api/users",
    methods=["POST"],
)
@auth_required
def create_user():
    data = UserSchema().load(request.json)
    user = User(name=data["name"], email=data["email"].lower())
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError as e:
        raise exceptions.UnprocessableEntity(
            "User already exists with this email"
        )

    return jsonify({})


# BUG: This seems to leave open stale SQLA sessions
