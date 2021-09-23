from .app import app
from .council import get_matters


@app.route("/healthz", methods=["GET"])
def healthz():
    return "Healthy!"


@app.route("/", methods=["GET"])
def home():
  matters = get_matters()
  return matters[0]
