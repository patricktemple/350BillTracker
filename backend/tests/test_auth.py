from uuid import uuid4

from freezegun import freeze_time

from src.app import app
from src.auth import auth_required, create_jwt
from src.models import db
from src.user.models import User


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


def test_expired_jwt__unauthorized(unauthenticated_client, user_id):
    user = User(id=user_id, name="test user", email="text@example.com")
    db.session.add(user)
    db.session.commit()

    with freeze_time("2000-1-1"):
        headers = {"Authorization": f"JWT {create_jwt(user_id)}"}
        response = unauthenticated_client.get(
            "/test/auth-required-endpoint", headers=headers
        )
        assert response.status_code == 200

    with freeze_time("2100-1-1"):
        response = unauthenticated_client.get(
            "/test/auth-required-endpoint", headers=headers
        )
        assert response.status_code == 401


def test_wrong_jwt_secret__unauthorized(unauthenticated_client, user_id):
    user = User(id=user_id, name="test user", email="text@example.com")
    db.session.add(user)
    db.session.commit()

    response = unauthenticated_client.get(
        "/test/auth-required-endpoint",
        headers={"Authorization": f"JWT {create_jwt(user_id)}"},
    )
    assert response.status_code == 200

    response = unauthenticated_client.get(
        "/test/auth-required-endpoint",
        headers={
            "Authorization": f"JWT {create_jwt(user_id, secret='wrong secret')}"
        },
    )
    assert response.status_code == 401


def test_public_endpoint__success(unauthenticated_client):
    response = unauthenticated_client.get("/test/public-endpoint")
    assert response.status_code == 200
