from .app import app
from .council import get_matters
from random import randrange


@app.route("/healthz", methods=["GET"])
def healthz():
    return "Healthy!"


@app.route("/", methods=["GET"])
def home():
  matters = get_matters()
  random_matter = matters[randrange(0, len(matters))]
  return f"Random matter: {random_matter['MatterName']}"