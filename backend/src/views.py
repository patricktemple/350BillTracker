from .app import app
from .council_api import get_recent_bills
from random import randrange


@app.route("/healthz", methods=["GET"])
def healthz():
    return "Healthy!"


@app.route("/", methods=["GET"])
def home():
  matters = get_recent_bills()
  random_matter = matters[randrange(0, len(matters))]
  return random_matter['MatterName']