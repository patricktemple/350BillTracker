import pytest

from src import app, models


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
