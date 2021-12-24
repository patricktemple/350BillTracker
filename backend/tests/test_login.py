import json
from datetime import datetime, timedelta
from unittest.mock import patch

from src.models import db
from src.user.models import LoginLink


@patch("src.ses.client")
def test_create_login_link_success(mock_boto3_client, client, user_email):
    response = client.post(
        "/api/create-login-link", data={"email": user_email}
    )
    assert response.status_code == 200
    mock_boto3_client.send_email.assert_called()


def test_create_login_link_user_not_found(client):
    response = client.post(
        "/api/create-login-link", data={"email": "nobody@example.com"}
    )
    assert response.status_code == 422


def test_login_success(client, user_id):
    login_link = LoginLink(
        user_id=user_id,
        token="foo",
        expires_at=datetime.now() + timedelta(days=1),
    )
    db.session.add(login_link)
    db.session.commit()

    response = client.post("/api/login", data={"token": "foo"})
    assert response.status_code == 200
    assert "authToken" in json.loads(response.data)


def test_login_token_expired(client, user_id):
    login_link = LoginLink(
        user_id=user_id,
        token="foo",
        expires_at=datetime.now() - timedelta(days=1),
    )
    db.session.add(login_link)
    db.session.commit()

    response = client.post("/api/login", data={"token": "foo"})
    assert response.status_code == 401


def test_login_token_not_found(client, user_id):
    response = client.post("/api/login", data={"token": "unknown"})
    assert response.status_code == 401
