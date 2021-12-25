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

# TODO: Can simplify this by just importing the views and letting the rest happen
from . import models, cron, views  # noqa: F401 isort:skip
from .bill import models as bill_models  # noqa: F401 isort:skip
from .bill import views as bill_views
from .person import views as person_views
from .sponsorship import views as sponsorship_views
from .user import views as user_views

from .person import models as person_models  # noqa: F401 isort:skip
from .sponsorship import models as sponsorship_models  # noqa: F401 isort:skip
from .user import models as user_models  # noqa: F401 isort:skip
