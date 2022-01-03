import logging
from uuid import uuid4

from flask import jsonify, request
from werkzeug import exceptions

from .. import state_api
from ..app import app
from ..auth import auth_required
from ..council_api import lookup_bill, lookup_bills
from ..council_sync import update_bill_sponsorships
from ..google_sheets import create_power_hour
from ..models import db
from .models import Bill, BillAttachment, CityBill, PowerHour
from .schema import (BillAttachmentSchema, BillSchema, CreatePowerHourSchema,
                     PowerHourSchema, StateBillSearchResultSchema,
                     TrackCityBillSchema)

# Views ----------------------------------------------------------------------

# TODO: Rename to not be saved-bills?
@app.route("/api/saved-bills", methods=["GET"])
@auth_required
def bills():
    bills = Bill.query.order_by(Bill.name).all()
    return BillSchema(many=True).jsonify(bills)


# TODO test
# TODO: have this autoload the sponsorships, attachments etc? and get rid of those endpoints perhaps
# TODO: Rename to not be saved-bills?
@app.route("/api/saved-bills/<uuid:bill_id>", methods=["GET"])
@auth_required
def get_bill(bill_id):
    bill = Bill.query.get(bill_id)
    return BillSchema().jsonify(bill)


# TODO: Rename to city-bills?
@app.route("/api/saved-bills", methods=["POST"])
@auth_required
def track_city_bill():
    data = TrackCityBillSchema().load(request.json)
    city_bill_id = data["city_bill_id"]
    if CityBill.query.filter_by(city_bill_id=city_bill_id).one_or_none():
        # There's a race condition of checking this and then inserting,
        # but in that rare case it will hit the DB unique constraint instead.
        raise exceptions.Conflict()

    bill_data = lookup_bill(city_bill_id)
    logging.info(
        f"Saving bill {city_bill_id}, council API returned {bill_data}"
    )

    bill = Bill(id=uuid4(), type=Bill.BillType.CITY, name=bill_data["name"], description=bill_data['description'])
    bill.city_bill = CityBill(**bill_data["city_bill"])
    db.session.add(bill)

    update_bill_sponsorships(bill.city_bill)

    db.session.commit()

    return jsonify({})


@app.route("/api/saved-bills/<uuid:bill_id>", methods=["PUT"])
@auth_required
def update_bill(bill_id):
    data = BillSchema().load(request.json)

    bill = Bill.query.get(bill_id)
    bill.notes = data["notes"]
    bill.nickname = data["nickname"]

    bill.twitter_search_terms = data["twitter_search_terms"]

    db.session.commit()

    return jsonify({})


@app.route("/api/saved-bills/<uuid:bill_id>", methods=["DELETE"])
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
    external_bills_ids = [
        b["city_bill"]["city_bill_id"] for b in external_bills
    ]
    tracked_bills = CityBill.query.filter(
        CityBill.city_bill_id.in_(external_bills_ids)
    ).all()
    tracked_bill_ids = set([t.city_bill_id for t in tracked_bills])

    for bill in external_bills:
        bill["tracked"] = bill["city_bill"]["city_bill_id"] in tracked_bill_ids

    return BillSchema(many=True).jsonify(external_bills)


# TODO figure out all these paths
@app.route("/api/state-bills/search", methods=["GET"])
@auth_required
def search_state_bills():
    code_name = request.args.get("codeName")
    session_year = request.args.get("sessionYear")
    result = state_api.search_bills(code_name, session_year)

    # TODO check which ones are already tracked

    return StateBillSearchResultSchema(many=True).jsonify(result)


@app.route("/api/saved-bills/<uuid:bill_id>/power-hours", methods=["GET"])
@auth_required
def bill_power_hours(bill_id):
    power_hours = (
        PowerHour.query.filter_by(bill_id=bill_id)
        .order_by(PowerHour.created_at)
        .all()
    )
    return PowerHourSchema(many=True).jsonify(power_hours)


@app.route(
    "/api/saved-bills/<uuid:bill_id>/power-hours",
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


@app.route("/api/saved-bills/<uuid:bill_id>/attachments", methods=["GET"])
@auth_required
def bill_attachments(bill_id):
    attachments = BillAttachment.query.filter_by(bill_id=bill_id).all()
    return BillAttachmentSchema(many=True).jsonify(attachments)


@app.route("/api/saved-bills/<uuid:bill_id>/attachments", methods=["POST"])
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
    "/api/saved-bills/-/attachments/<uuid:attachment_id>", methods=["DELETE"]
)
@auth_required
def delete_bill_attachment(attachment_id):
    attachment = BillAttachment.query.filter_by(id=attachment_id).one()
    db.session.delete(attachment)
    db.session.commit()

    return jsonify({})
