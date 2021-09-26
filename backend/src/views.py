from flask import jsonify, render_template, request
from marshmallow import fields

from .app import app
from .app import marshmallow as ma
from .council_api import lookup_bills
from .council_sync import add_or_update_bill, convert_matter_to_bill, update_sponsorships
from .models import Bill, Legislator, db, BillSponsorship, BillAttachment


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
@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def index(path):
    return render_template("index.html")


# Bills ----------------------------------------------------------------------


class BillSchema(CamelCaseSchema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    title = fields.String(required=True)
    status = fields.String(required=True)
    body = fields.String(required=True)
    file = fields.String(required=True)
    tracked = fields.Boolean()
    notes = fields.String()
    nickname = fields.String()


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


class UpdateBillSchema(CamelCaseSchema):
    notes = fields.String(required=True)
    nickname = fields.String(required=True)


@app.route("/api/saved-bills/<int:bill_id>", methods=["PUT"])
def update_bill(bill_id):
    data = UpdateBillSchema().load(request.json)

    bill = Bill.query.get(bill_id)
    bill.notes = data['notes']
    bill.nickname = data['nickname']

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


# Council members ----------------------------------------------------------------------


class CouncilMemberSchema(CamelCaseSchema):
    name = fields.String(required=True)
    id = fields.Integer(required=True)
    term_start = fields.DateTime()
    term_end = fields.DateTime()
    email = fields.String()
    district_phone = fields.String()
    legislative_phone = fields.String()
    borough = fields.String()
    website = fields.String()
    notes = fields.String()


class SingleMemberSponsorshipsSchema(CamelCaseSchema):
    legislator_id = fields.Integer(required=True)
    bill = fields.Nested(BillSchema)


@app.route("/api/council-members", methods=["GET"])
def get_council_members():
    legislators = Legislator.query.order_by(Legislator.name).all()
    return CouncilMemberSchema(many=True).jsonify(legislators)


class UpdateCouncilMemberSchema(CamelCaseSchema):
    notes = fields.String(required=True)


@app.route("/api/council-members/<int:legislator_id>", methods=["PUT"])
def update_council_member(legislator_id):
    data = UpdateCouncilMemberSchema().load(request.json)

    legislator = Legislator.query.get(legislator_id)
    legislator.notes = data['notes']

    db.session.commit()

    return jsonify({})


@app.route("/api/council-members/<int:legislator_id>/sponsorships", methods=["GET"])
def council_member_sponsorships(legislator_id):
    # TODO: No need to wrap this object, just return the list of sponsor people?
    sponsorships = BillSponsorship.query.filter_by(legislator_id=legislator_id).all()
    return SingleMemberSponsorshipsSchema(many=True).jsonify(sponsorships)


# Bill sponsorships ----------------------------------------------------------------------
class SingleBillSponsorshipsSchema(CamelCaseSchema):
    bill_id = fields.Integer(required=True)
    legislator = fields.Nested(CouncilMemberSchema)


@app.route("/api/saved-bills/<int:bill_id>/sponsorships", methods=["GET"])
def bill_sponsorships(bill_id):
    # TODO: No need to wrap this object, just return the list of sponsor people?
    sponsorships = BillSponsorship.query.filter_by(bill_id=bill_id).all()
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
        url=data['url'],
        name=data['name'],
    )
    db.session.add(attachment)
    db.session.commit()

    return jsonify({})


# BUG: This seems to leave open stale SQLA sessions