from flask import render_template

from .app import app


@app.route("/healthz", methods=["GET"])
def healthz():
    return "Healthy!"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    return render_template("index.html")


# BUG: This seems to leave open stale SQLA sessions
