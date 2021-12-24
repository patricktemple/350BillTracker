import json

import responses

from src import app
from src.bill.models import DEFAULT_TWITTER_SEARCH_TERMS, Bill
from src.person.models import Legislator
from src.models import db
from src.utils import now

from .utils import assert_response


def create_fake_matter(matter_id):
    return {
        "MatterId": matter_id,
        "MatterFile": "fake matter file",
        "MatterName": "fake matter name",
        "MatterTitle": "fake matter title",
        "MatterBodyName": "fake matter body",
        "MatterIntroDate": "2021-01-06T00:00:00",
        "MatterStatusName": "fake matter status",
    }


def test_get_bills_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get("/api/saved-bills")
    assert response.status_code == 401


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
                "twitterSearchTerms": DEFAULT_TWITTER_SEARCH_TERMS,
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
        data={
            "notes": "good bill",
            "nickname": "skip the stuff",
            "twitterSearchTerms": ["oil"],
        },
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
                "twitterSearchTerms": ["oil"],
            }
        ],
    )


@responses.activate
def test_save_bill(client):
    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters/123?token=fake_token",
        json=create_fake_matter(123),
    )

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters/123/sponsors?token=fake_token",
        json=[{"MatterSponsorNameId": 99, "MatterSponsorSequence": 0}],
    )

    non_sponsor = Legislator(id=88, name="Non sponsor")
    db.session.add(non_sponsor)

    sponsor = Legislator(id=99, name="Sponsor")
    db.session.add(sponsor)

    response = client.post(
        "/api/saved-bills",
        data={"id": "123"},
    )
    assert response.status_code == 200

    bill = Bill.query.one()
    assert bill.id == 123

    assert len(bill.sponsorships) == 1
    assert bill.sponsorships[0].legislator.name == "Sponsor"
    assert not bill.sponsorships[0].added_at


@responses.activate
def test_save_bill__already_exists(client):
    bill = Bill(
        id=1, name="name", file="file", title="title", intro_date=now()
    )
    db.session.add(bill)
    db.session.commit()

    response = client.post(
        "/api/saved-bills",
        data={"id": "1"},
    )
    assert response.status_code == 409


@responses.activate
def test_lookup_bill_not_tracked(client):
    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters?token=fake_token&%24filter=MatterTypeName+eq+%27Introduction%27+and+substringof%28%271234%27%2C+MatterFile%29+eq+true",
        json=[create_fake_matter(1)],
    )

    response = client.get(
        "/api/search-bills?file=1234",
    )
    # assert more fields?
    assert response.status_code == 200
    response_data = json.loads(response.data)[0]
    assert response_data["id"] == 1
    assert response_data["tracked"] == False


@responses.activate
def test_lookup_bill_already_tracked(client):
    bill = Bill(
        id=1, file="file", name="name", title="title", intro_date=now()
    )
    db.session.add(bill)
    db.session.commit()

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters?token=fake_token&%24filter=MatterTypeName+eq+%27Introduction%27+and+substringof%28%271234%27%2C+MatterFile%29+eq+true",
        json=[create_fake_matter(1)],
    )

    response = client.get(
        "/api/search-bills?file=1234",
    )
    # assert more fields?
    assert response.status_code == 200
    response_data = json.loads(response.data)[0]
    assert response_data["id"] == 1
    assert response_data["tracked"] == True
