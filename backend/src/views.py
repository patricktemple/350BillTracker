from flask import jsonify, render_template, request
from marshmallow import fields

from .app import app
from .app import marshmallow as ma
from .council_sync import add_or_update_bill, convert_matter_to_bill
from .models import Bill, Person


@app.route("/healthz", methods=["GET"])
def healthz():
    return "Healthy!"


@app.route("/")
def index():
    return render_template("index.html")


# Bills ----------------------------------------------------------------------


class BillSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    title = fields.String(required=True)
    status = fields.String(required=True)
    body = fields.Body(required=True)


@app.route("/saved-bills", methods=["GET"])
def bills():
    bills = Bill.query.all()
    return BillSchema(many=True).jsonify(bills)


@app.route("/saved-bills", methods=["POST"])
def save_bill():
    matter_id = request.json["id"]
    add_or_update_bill(matter_id)
    return jsonify({})


@app.route("/search-bills", methods=["GET"])
def search_bills():
    file = request.args.get("file")

    bills = lookup_bills(file)

    return BillSchema().jsonify([convert_matter_to_bill(b) for b in bills])


# Council members ----------------------------------------------------------------------


class CouncilMemberSchema(ma.Schema):
    name = fields.String(required=True)
    id = fields.Integer(required=True)
    term_start = fields.DateTime()
    term_end = fields.DateTime()


@app.route("/council-members", methods=["GET"])
def get_council_members():
    persons = Person.query.all()
    return CouncilMemberSchema(many=True).jsonify(persons)
