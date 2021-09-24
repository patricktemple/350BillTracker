import json
from random import randrange
from flask import render_template, request

from .app import app
from .council_api import get_recent_bills, lookup_bills
from .council_sync import convert_matter_to_bill, add_or_update_bill
from .models import Bill


@app.route("/healthz", methods=["GET"])
def healthz():
    return "Healthy!"


@app.route("/random", methods=["GET"])
def random():
    matters = get_recent_bills()
    random_matter = matters[randrange(0, len(matters))]
    return random_matter["MatterName"]
  

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/saved-bills", methods=["GET"])
def bills():
    # TODO: Use marshmallow
    bills = Bill.query.all()
    return json.dumps(
        [
            {
                "name": b.name,
                "title": b.title,
                "file": b.file,
                "status": b.status,
                "body": b.body,
            }
            for b in bills
        ]
    )


@app.route("/saved-bills", methods=["POST"])
def save_bill():
    matter_id = request.json['id']
    add_or_update_bill(matter_id)
    return "{}"


@app.route("/search-bills", methods=["GET"])
def search_bills():
    file = request.args.get("file")

    bills = lookup_bills(file)

    return json.dumps(
        [convert_matter_to_bill(b) for b in bills]
    )