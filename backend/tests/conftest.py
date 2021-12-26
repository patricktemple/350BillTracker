from uuid import uuid4

import pytest

from src import app, models
from src.bill.models import Bill, CityBill, db
from src.user.models import User
from src.utils import now

from .utils import ApiClient


@pytest.fixture(autouse=True)
def autouse_fixtures():
    models.db.drop_all()
    models.db.create_all()

    yield

    models.db.session.close()


# TODO: Do we want this?
# @pytest.fixture(autouse=True)
# def request_context(app):
#     with app.test_request_context():
#         yield


@pytest.fixture
def bill():
    bill = Bill(id=uuid4(), name="name", type=Bill.BillType.CITY)
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        title="title",
        intro_date=now(),
        status="Enacted",
        active_version="A",
    )
    db.session.add(bill)
    return bill


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def user_email():
    return "test@example.com"


@pytest.fixture
def user_name():
    return "Test user"


@pytest.fixture
def client(user_id, user_email, user_name):
    app.app.test_client_class = ApiClient
    with app.app.test_client() as client:
        user = User(id=user_id, name=user_name, email=user_email)
        models.db.session.add(user)
        models.db.session.commit()

        client.set_authenticated_user_id(user_id)
        yield client


@pytest.fixture
def unauthenticated_client():
    app.app.test_client_class = ApiClient
    with app.app.test_client() as client:
        yield client
