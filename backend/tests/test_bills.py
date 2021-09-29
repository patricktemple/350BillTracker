import json

from src import app
from src.models import Bill, db
from src.utils import now

from .utils import assert_response


def test_get_saved_bills(client):
    bill = Bill(
        id=1,
        name="name",
        file="file",
        title="title",
        intro_date=now(),
        nickname="ban gas",
        status="Enacted",
        notes="Good job everyone",
        body="Committee on environment",
    )
    db.session.add(bill)
    db.session.commit()

    response = client.get("/api/saved-bills")
    assert_response(
        response,
        200,
        [
            {
                "body": "Committee on environment",
                "file": "file",
                "id": 1,
                "name": "name",
                "nickname": "ban gas",
                "notes": "Good job everyone",
                "status": "Enacted",
                "title": "title",
                "tracked": True,
            }
        ],
    )


def test_delete_bill(client):
    bill = Bill(
        id=1, name="name", file="file", title="title", intro_date=now()
    )
    db.session.add(bill)
    db.session.commit()

    response = client.get("/api/saved-bills")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1

    response = client.delete("/api/saved-bills/1")
    assert response.status_code == 200

    response = client.get("/api/saved-bills")
    assert_response(response, 200, [])


def test_update_bill(client):
    bill = Bill(
        id=1, name="name", file="file", title="title", intro_date=now()
    )
    db.session.add(bill)
    db.session.commit()

    response = client.put(
        "/api/saved-bills/1",
        data={"notes": "good bill", "nickname": "skip the stuff"},
    )
    assert response.status_code == 200

    response = client.get("/api/saved-bills")
    assert_response(
        response,
        200,
        [
            {
                "body": None,
                "file": "file",
                "id": 1,
                "name": "name",
                "nickname": "skip the stuff",
                "notes": "good bill",
                "status": None,
                "title": "title",
                "tracked": True,
            }
        ],
    )


# TODO test coverage:
# Tracking a new bill
# Searching for bill in council API
# Getting sponsorships
# Adding/deleting attachments
