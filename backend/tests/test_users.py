from src.models import User, db

from .utils import assert_response


def test_get_users(client, user_id, user_name, user_email):
    response = client.get("/api/users")

    # There's one test user already created in the fixture
    assert_response(
        response,
        200,
        [{"name": user_name, "email": user_email, "id": str(user_id)}],
    )


def test_create_user_success(client, user_id):
    response = client.post(
        "/api/users",
        data={"name": "Second user", "email": "second@example.com"},
    )
    assert response.status_code == 200

    user = User.query.filter(User.id != user_id).one()
    assert user.name == "Second user"
    assert user.email == "second@example.com"


def test_invite_user_email_exists(client, user_email):
    response = client.post(
        "/api/users", data={"name": "Second user", "email": user_email}
    )
    assert response.status_code == 422

    # Should be case insensitive
    response = client.post(
        "/api/users", data={"name": "Second user", "email": user_email.upper()}
    )
    assert response.status_code == 422


def test_delete_user_success(client, user_id):
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 200


def test_delete_user_cant_be_deleted(client):
    new_user = User(
        name="Non deletable", email="someone@example.com", can_be_deleted=False
    )
    db.session.add(new_user)
    db.session.commit()

    response = client.delete(f"/api/users/{new_user.id}")
    assert response.status_code == 422