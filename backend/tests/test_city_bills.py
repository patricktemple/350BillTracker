import json
from uuid import uuid4

import responses
from src.bill.models import DEFAULT_TWITTER_SEARCH_TERMS, Bill, CityBill, UserBillSettings
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
    response = unauthenticated_client.get("/api/bills")
    assert response.status_code == 401


def test_get_saved_bills(client):
    bill = Bill(
        name="name",
        description="description",
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
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()

    response = client.get("/api/bills")
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
                    "status": "Enacted",
                    "sponsorCount": 0,
                },
                "codeName": "file",
                "displayName": "ban gas",
                "status": "Enacted",
                "name": "name",
                "description": "description",
                "nickname": "ban gas",
                "notes": "Good job everyone",
                "twitterSearchTerms": DEFAULT_TWITTER_SEARCH_TERMS,
                "stateBill": None,
            }
        ],
    )


def test_delete_bill(client):
    bill = Bill(
        name="name", description="description", type=Bill.BillType.CITY
    )
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        status="Enacted",
        intro_date=now(),
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()

    response = client.get("/api/bills")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1

    response = client.delete(f"/api/bills/{bill.id}")
    assert response.status_code == 200

    response = client.get("/api/bills")
    assert_response(response, 200, [])


def test_update_bill(client):
    bill_id = uuid4()
    bill = Bill(
        id=bill_id,
        name="name",
        description="description",
        type=Bill.BillType.CITY,
    )
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        status="Enacted",
        intro_date=now(),
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()

    response = client.put(
        f"/api/bills/{bill.id}",
        data={
            "notes": "good bill",
            "nickname": "skip the stuff",
            "twitterSearchTerms": ["oil"],
        },
    )
    assert response.status_code == 200

    response = client.get("/api/bills")
    assert_response(
        response,
        200,
        [
            {
                "id": str(bill_id),
                "type": "CITY",
                "description": "description",
                "stateBill": None,
                "cityBill": {
                    "cityBillId": 1,
                    "councilBody": None,
                    "file": "file",
                    "status": "Enacted",
                    "sponsorCount": 0,
                },
                "codeName": "file",
                "status": "Enacted",
                "name": "name",
                "nickname": "skip the stuff",
                "notes": "good bill",
                "displayName": "skip the stuff",
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
        "/api/city-bills/track",
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
    bill = Bill(
        name="name", description="description", type=Bill.BillType.CITY
    )
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        intro_date=now(),
        status="Committee",
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()

    response = client.post(
        "/api/city-bills/track",
        data={"cityBillId": 1},
    )
    assert response.status_code == 409


@responses.activate
def test_lookup_bill_not_tracked(client):
    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters?token=fake_token&%24filter=%28MatterTypeName+eq+%27Introduction%27%29+and+%28substringof%28%271234%27%2C+MatterFile%29+eq+true%29",
        json=[create_fake_matter(1)],
    )

    response = client.get(
        "/api/city-bills/search?file=1234",
    )
    assert response.status_code == 200
    response_data = json.loads(response.data)[0]
    assert response_data["type"] == "CITY"
    assert response_data["cityBill"]["cityBillId"] == 1
    assert response_data["tracked"] == False

    # TODO: Consider switching these tests over to snapshots to capture more info?


@responses.activate
def test_lookup_bill_already_tracked(client):
    bill = Bill(
        name="name", description="description", type=Bill.BillType.CITY
    )
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        intro_date=now(),
        status="Enacted",
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters?token=fake_token&%24filter=%28MatterTypeName+eq+%27Introduction%27%29+and+%28substringof%28%271234%27%2C+MatterFile%29+eq+true%29",
        json=[create_fake_matter(1)],
    )

    response = client.get(
        "/api/city-bills/search?file=1234",
    )
    # assert more fields?
    assert response.status_code == 200
    response_data = json.loads(response.data)[0]
    assert response_data["cityBill"]["cityBillId"] == 1
    assert response_data["tracked"] == True


def test_update_bill_settings__no_explicit_setting(client, city_bill, user_id):
    client.put(
        f"/api/bills/{city_bill.id}/viewer-settings", data={
            "sendBillUpdateNotifications": True
        }
    )
    bill_settings = UserBillSettings.query.filter_by(bill_id=city_bill.id, user_id=user_id).one()
    assert bill_settings.send_bill_update_notifications


def test_update_bill_settings__setting_already_exists(client, city_bill, user_id):
    existing_settings = UserBillSettings(bill_id=city_bill.id, user_id=user_id, send_bill_update_notifications=False)
    db.session.add(existing_settings)
    db.session.commit()

    client.put(
        f"/api/bills/{city_bill.id}/viewer-settings", data={
            "sendBillUpdateNotifications": True
        }
    )
    bill_settings = UserBillSettings.query.filter_by(bill_id=city_bill.id, user_id=user_id).one()
    assert bill_settings.send_bill_update_notifications