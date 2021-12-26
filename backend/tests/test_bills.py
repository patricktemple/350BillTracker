import json
from uuid import uuid4

import responses

from src.bill.models import DEFAULT_TWITTER_SEARCH_TERMS, Bill, CityBill
from src.models import db
from src.person.models import CouncilMember, Person
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
        "MatterVersion": "A",
    }


def test_get_bills_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get("/api/saved-bills")
    assert response.status_code == 401


def test_get_saved_bills(client):
    bill = Bill(
        name="name",
        nickname="ban gas",
        notes="Good job everyone",
        type=Bill.BillType.CITY,
    )
    bill.city_bill = CityBill(
        file="file",
        city_bill_id=1,
        council_body="Committee on environment",
        status="Enacted",
        intro_date=now(),
        title="title",
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()

    response = client.get("/api/saved-bills")
    assert_response(
        response,
        200,
        [
            {
                "id": str(bill.id),
                "type": "CITY",
                "tracked": True,
                "cityBill": {
                    "cityBillId": 1,
                    "councilBody": "Committee on environment",
                    "file": "file",
                    "title": "title",
                    "status": "Enacted",
                },
                "name": "name",
                "nickname": "ban gas",
                "notes": "Good job everyone",
                "twitterSearchTerms": DEFAULT_TWITTER_SEARCH_TERMS,
                "stateBill": None,
            }
        ],
    )


def test_delete_bill(client):
    bill = Bill(name="name", type=Bill.BillType.CITY)
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        title="title",
        status="Enacted",
        intro_date=now(),
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()

    response = client.get("/api/saved-bills")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1

    response = client.delete(f"/api/saved-bills/{bill.id}")
    assert response.status_code == 200

    response = client.get("/api/saved-bills")
    assert_response(response, 200, [])


def test_update_bill(client):
    bill_id = uuid4()
    bill = Bill(id=bill_id, name="name", type=Bill.BillType.CITY)
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        title="title",
        status="Enacted",
        intro_date=now(),
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()

    response = client.put(
        f"/api/saved-bills/{bill.id}",
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
                "id": str(bill_id),
                "type": "CITY",
                "stateBill": None,
                "cityBill": {
                    "cityBillId": 1,
                    "councilBody": None,
                    "file": "file",
                    "status": "Enacted",
                    "title": "title",
                },
                "name": "name",
                "nickname": "skip the stuff",
                "notes": "good bill",
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
        json=[
            {
                "MatterSponsorNameId": 99,
                "MatterSponsorSequence": 0,
                "MatterSponsorMatterVersion": "A",
            }
        ],
    )

    non_sponsor = Person(
        name="Non sponsor", type=Person.PersonType.COUNCIL_MEMBER
    )
    non_sponsor.council_member = CouncilMember(city_council_person_id=88)
    db.session.add(non_sponsor)

    sponsor = Person(name="Sponsor", type=Person.PersonType.COUNCIL_MEMBER)
    sponsor.council_member = CouncilMember(city_council_person_id=99)
    db.session.add(sponsor)

    response = client.post(
        "/api/saved-bills",
        data={"cityBillId": 123},
    )
    assert response.status_code == 200

    bill = Bill.query.one()
    assert bill.type == Bill.BillType.CITY
    assert bill.city_bill.city_bill_id == 123

    assert len(bill.city_bill.sponsorships) == 1
    assert (
        bill.city_bill.sponsorships[0].council_member.person.name == "Sponsor"
    )
    assert not bill.city_bill.sponsorships[0].added_at


@responses.activate
def test_save_bill__already_exists(client):
    bill = Bill(name="name", type=Bill.BillType.CITY)
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        title="title",
        intro_date=now(),
        status="Committee",
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()

    response = client.post(
        "/api/saved-bills",
        data={"cityBillId": 1},
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
    print(response_data)
    assert response_data["type"] == "CITY"
    assert response_data["cityBill"]["cityBillId"] == 1
    assert response_data["tracked"] == False

    # TODO: Consider switching these tests over to snapshots to capture more info?


@responses.activate
def test_lookup_bill_already_tracked(client):
    bill = Bill(name="name", type=Bill.BillType.CITY)
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        title="title",
        intro_date=now(),
        status="Enacted",
        active_version="A",
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
    assert response_data["cityBill"]["cityBillId"] == 1
    assert response_data["tracked"] == True
