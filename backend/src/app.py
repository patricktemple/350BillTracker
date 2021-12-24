import logging

from flask import Flask
from flask_marshmallow import Marshmallow

from .settings import DATABASE_URL

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

marshmallow = Marshmallow(app)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

from . import models, cron, views  # noqa: F401 isort:skip
from .bill import views as bill_views  # noqa: F401 isort:skip
from .legislator import views as legislator_views  # noqa: F401 isort:skip
from .sponsorship import views as sponsorship_views  # noqa: F401 isort:skip
from .user import views as user_views  # noqa: F401 isort:skip
