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
def client():
    # db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    # flaskr.app.config['TESTING'] = True

    app.app.test_client_class = ApiClient
    with app.app.test_client() as client:
        yield client
