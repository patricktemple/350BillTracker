from uuid import uuid4

import pytest

from src import app, models
from src.bill.models import (AssemblyBill, Bill, CityBill, SenateBill,
                             StateBill, db)
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
def city_bill():
    bill = Bill(id=uuid4(), name="name", description="description", nickname="nickname", type=Bill.BillType.CITY)
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        intro_date=now(),
        status="Enacted",
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()
    return bill


@pytest.fixture
def state_bill():
    bill = Bill(id=uuid4(), name="state bill", description="description", nickname="nickname", type=Bill.BillType.STATE)
    bill.state_bill = StateBill(
        session_year=2021,
    )
    bill.state_bill.senate_bill = SenateBill(base_print_no="S1234", active_version="", status="Committee")
    bill.state_bill.assembly_bill = AssemblyBill(base_print_no="A1234", active_version="A", status="Voted")
    db.session.add(bill)
    db.session.commit()
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
