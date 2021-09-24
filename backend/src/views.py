from flask import jsonify, render_template, request
from marshmallow import fields

from .app import app
from .app import marshmallow as ma
from .council_api import lookup_bills
from .council_sync import add_or_update_bill, convert_matter_to_bill
from .models import Bill, Legislator


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
@app.route("/")
def index():
    return render_template("index.html")


# Bills ----------------------------------------------------------------------


class BillSchema(CamelCaseSchema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    title = fields.String(required=True)
    status = fields.String(required=True)
    body = fields.String(required=True)


@app.route("/api/saved-bills", methods=["GET"])
def bills():
    bills = Bill.query.all()
    return BillSchema(many=True).jsonify(bills)


@app.route("/api/saved-bills", methods=["POST"])
def save_bill():
    matter_id = request.json["id"]
    add_or_update_bill(matter_id)
    return jsonify({})


@app.route("/api/search-bills", methods=["GET"])
def search_bills():
    file = request.args.get("file")

    bills = lookup_bills(file)

    return BillSchema().jsonify([convert_matter_to_bill(b) for b in bills])


# Council members ----------------------------------------------------------------------


class CouncilMemberSchema(CamelCaseSchema):
    name = fields.String(required=True)
    id = fields.Integer(required=True)
    term_start = fields.DateTime()
    term_end = fields.DateTime()
    email = fields.String()
    district_phone = fields.String()
    legislative_phone = fields.String()


@app.route("/api/council-members", methods=["GET"])
def get_council_members():
    legislators = Legislator.query.all()
    return CouncilMemberSchema(many=True).jsonify(legislators)
