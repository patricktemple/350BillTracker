from uuid import uuid4

import pytest

from src import app, models

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
def user_id():
    return uuid4()


@pytest.fixture
def user_email():
    return "text@example.com"


@pytest.fixture
def client(user_id, user_email):
    app.app.test_client_class = ApiClient
    with app.app.test_client() as client:
        user = models.User(id=user_id, name="Test user", email=user_email)
        models.db.session.add(user)
        models.db.session.commit()

        client.set_authenticated_user_id(user_id)
        yield client


@pytest.fixture
def unauthenticated_client():
    app.app.test_client_class = ApiClient
    with app.app.test_client() as client:
        yield client
