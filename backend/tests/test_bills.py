from src import app
from src.models import Bill, db
from src.utils import now

from .utils import assert_response


def test_create_bill(client):
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
