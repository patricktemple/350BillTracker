from random import randrange

from .app import app
from .models import Bill
from .council_api import get_recent_bills
import json


@app.route("/healthz", methods=["GET"])
def healthz():
    return "Healthy!"


@app.route("/", methods=["GET"])
def home():
    matters = get_recent_bills()
    random_matter = matters[randrange(0, len(matters))]
    return random_matter["MatterName"]


@app.route("/bills", methods=["GET"])
def bills():
    bills = Bill.query.all()
    return json.dumps([{
      "name": b.name,
      "title": b.title,
      "file": b.file,
      "status": b.status,
      "body": b.body,
    } for b in bills] )