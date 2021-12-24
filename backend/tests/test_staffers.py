from uuid import uuid4

from src import app
from src.legislator.models import Legislator, Staffer
from src.models import db

from .utils import assert_response


def test_get_legislator_staffers(client):
    staffer_id = uuid4()
    legislator = Legislator(id=1, name="name")
    staffer = Staffer(
        id=staffer_id,
        name="staffer",
        title="chief of staff",
        email="test@example.com",
        twitter="TheChief",
        phone="111-111-1111",
    )
    legislator.staffers.append(staffer)
    db.session.add(legislator)
    db.session.commit()

    response = client.get("/api/legislators/1/staffers")
    assert_response(
        response,
        200,
        [
            {
                "email": "test@example.com",
                "id": str(staffer_id),
                "name": "staffer",
                "phone": "111-111-1111",
                "title": "chief of staff",
                "twitter": "TheChief",
            }
        ],
    )


def test_add_legislator_staffer(client):
    legislator = Legislator(id=1, name="name")
    db.session.add(legislator)
    db.session.commit()

    response = client.post(
        "/api/legislators/1/staffers",
        data={
            "name": "staffer",
            "title": "chief of staff",
            "twitter": "TheChief",
            "phone": "111-111-1111",
            "email": "test@example.com",
        },
    )
    assert response.status_code == 200

    staffer = Staffer.query.one()
    assert staffer.name == "staffer"
    assert staffer.title == "chief of staff"
    assert staffer.twitter == "TheChief"
    assert staffer.phone == "111-111-1111"
    assert staffer.email == "test@example.com"


def test_add_legislator_invalid_twitter(client):
    legislator = Legislator(id=1, name="name")
    db.session.add(legislator)
    db.session.commit()

    response = client.post(
        "/api/legislators/1/staffers",
        data={
            "name": "staffer",
            "twitter": "&@89)(",
        },
    )
    assert response.status_code == 422


def test_delete_bill_attachment(client):
    staffer_id = uuid4()
    legislator = Legislator(id=1, name="name")
    staffer = Staffer(
        id=staffer_id,
        name="staffer",
    )
    legislator.staffers.append(staffer)
    db.session.add(legislator)
    db.session.commit()

    client.delete(f"/api/legislators/-/staffers/{staffer_id}")

    staffers = Staffer.query.all()
    assert len(staffers) == 0
