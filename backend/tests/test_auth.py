from uuid import uuid4

from src.app import app
from src.auth import auth_required


@app.route(
    "/test/auth-required-endpoint",
    methods=["GET"],
)
@auth_required
def auth_required_endpoint():
    return "Hello"


@app.route(
    "/test/public-endpoint",
    methods=["GET"],
)
def public_endpoint():
    return "Hello"


def test_no_jwt__unauthorized(unauthenticated_client):
    response = unauthenticated_client.get("/test/auth-required-endpoint")
    assert response.status_code == 401


def test_jwt_for_nonexistent_user__forbidden(unauthenticated_client):
    unauthenticated_client.set_authenticated_user_id(uuid4())
    response = unauthenticated_client.get("/test/auth-required-endpoint")
    assert response.status_code == 403


def test_authenticated_client__success(client):
    response = client.get("/test/auth-required-endpoint")
    assert response.status_code == 200


def test_expired_jwt__unauthorized():
    pass


def test_wrong_jwt_secret__unauthorized():
    pass


def test_public_endpoint__success(unauthenticated_client):
    response = unauthenticated_client.get("/test/public-endpoint")
    assert response.status_code == 200
