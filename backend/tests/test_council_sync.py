from datetime import datetime, timezone

import responses
from freezegun import freeze_time

from src.bill.models import Bill
from src.council_sync import (
    add_council_members,
    fill_council_person_data_from_api,
    fill_council_person_static_data,
    sync_bill_updates,
    update_all_sponsorships,
)
from src.person.models import Legislator
from src.models import db
from src.sponsorship.models import BillSponsorship
from src.static_data import STATIC_DATA_BY_LEGISLATOR_ID


@responses.activate
@freeze_time("2021-10-12")
def test_add_council_members():
    existing_legislator = Legislator(
        id=1, name="Corey Johnson", term_start="2000-01-01"
    )
    db.session.add(existing_legislator)

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/officerecords?token=fake_token&%24filter=OfficeRecordBodyName+eq+%27City+Council%27+and+OfficeRecordStartDate+le+datetime%272021-10-12%27+and+OfficeRecordEndDate+ge+datetime%272021-10-12%27",
        json=[
            {
                "OfficeRecordFullName": "Corey Johnson the 2nd",
                "OfficeRecordPersonId": "1",
                "OfficeRecordStartDate": "2021-01-01",
                "OfficeRecordEndDate": "2022-01-01",
            },
            {
                "OfficeRecordFullName": "Brad Lander",
                "OfficeRecordPersonId": "2",
                "OfficeRecordStartDate": "2021-01-01",
                "OfficeRecordEndDate": "2022-01-01",
            },
        ],
    )

    add_council_members()

    assert Legislator.query.count() == 2

    corey_johnson = Legislator.query.get(1)
    assert corey_johnson.name == "Corey Johnson the 2nd"
    assert corey_johnson.term_start == datetime(
        2021, 1, 1, tzinfo=timezone.utc
    )
    assert corey_johnson.term_end == datetime(2022, 1, 1, tzinfo=timezone.utc)

    brad_lander = Legislator.query.get(2)
    assert brad_lander.name == "Brad Lander"


@responses.activate
def test_fill_council_person_data():
    legislator_to_update = Legislator(id=1, name="Corey Johnson")
    db.session.add(legislator_to_update)

    legislator_without_new_data = Legislator(
        id=2, name="Person who was impeached and removed"
    )
    db.session.add(legislator_without_new_data)

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/persons/1?token=fake_token",
        json={
            "PersonEmail": "corey@council.nyc.gov",
            "PersonPhone": "555-111-1111",
            "PersonPhone2": "888-888-8888",
            "PersonCity1": "New York",
            "PersonWWW": "https://www.example.com/",
        },
    )

    # We just want to check that a 404 doesn't crash the whole thing
    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/persons/2?token=fake_token",
        status=404,
    )

    fill_council_person_data_from_api()

    assert Legislator.query.count() == 2
    corey = Legislator.query.get(1)
    assert corey.email == "corey@council.nyc.gov"
    assert corey.district_phone == "555-111-1111"
    assert corey.legislative_phone == "888-888-8888"
    assert corey.website == "https://www.example.com/"


def test_fill_council_person_static_data():
    corey_static = STATIC_DATA_BY_LEGISLATOR_ID[7631]
    legislator_to_update = Legislator(
        id=7631,
        name="Corey Johnson badly formatted name----",
        email="existing-email@council.nyc.gov",
    )
    db.session.add(legislator_to_update)

    legislator_without_static_data = Legislator(
        id=2, name="Person without static data"
    )
    db.session.add(legislator_without_static_data)

    fill_council_person_static_data()

    corey = Legislator.query.get(7631)
    assert corey.name == corey_static["name"]
    assert corey.twitter == corey_static["twitter"]
    assert corey.party == corey_static["party"]
    assert corey.borough == corey_static["borough"]
    assert corey.email == "existing-email@council.nyc.gov"


@responses.activate
def test_sync_bill_updates():
    bill = Bill(
        id=1,
        file="Intro 200",
        name="Electric school buses",
        title="Bill title",
        status="Committee",
        intro_date="2000-1-1",
        nickname="Shouldn't change",
    )
    db.session.add(bill)

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters/1?token=fake_token",
        json={
            "MatterId": "1",
            "MatterFile": "New file",
            "MatterName": "New name",
            "MatterTitle": "New title",
            "MatterBodyName": "New body",
            "MatterIntroDate": "2021-01-01T00:00:00",
            "MatterStatusName": "New status",
        },
    )

    sync_bill_updates()

    result = Bill.query.one()
    assert result.name == "New name"
    assert result.title == "New title"
    assert result.file == "New file"
    assert result.body == "New body"
    assert result.status == "New status"
    assert result.intro_date == datetime(2021, 1, 1, tzinfo=timezone.utc)
    assert result.nickname == "Shouldn't change"


@responses.activate
@freeze_time("2021-1-1")
def test_update_sponsorships__new_sponsor():
    bill = Bill(
        id=1,
        file="Intro 200",
        name="Electric school buses",
        title="Bill title",
        status="Committee",
        intro_date="2000-1-1",
    )
    db.session.add(bill)
    legislator = Legislator(id=1, name="Patrick")
    db.session.add(legislator)

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters/1/sponsors?token=fake_token",
        json=[
            {"MatterSponsorNameId": 1, "MatterSponsorSequence": 0},
            {
                # This one isn't found in the DB
                "MatterSponsorNameId": 2,
                "MatterSponsorSequence": 1,
            },
        ],
    )

    update_all_sponsorships()

    sponsorship = BillSponsorship.query.one()
    assert sponsorship.legislator_id == 1
    assert sponsorship.bill_id == 1
    assert sponsorship.added_at == datetime(2021, 1, 1, tzinfo=timezone.utc)


@responses.activate
@freeze_time("2021-1-1")
def test_update_sponsorships__sponsorship_already_exists():
    bill = Bill(
        id=1,
        file="Intro 200",
        name="Electric school buses",
        title="Bill title",
        status="Committee",
        intro_date="2000-1-1",
    )
    db.session.add(bill)
    legislator = Legislator(id=1, name="Patrick")
    db.session.add(legislator)

    sponsorship = BillSponsorship(
        bill_id=1,
        legislator_id=1,
        added_at=datetime(2000, 1, 1, tzinfo=timezone.utc),
    )
    db.session.add(sponsorship)

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters/1/sponsors?token=fake_token",
        json=[{"MatterSponsorNameId": 1, "MatterSponsorSequence": 0}],
    )

    update_all_sponsorships()

    sponsorship = BillSponsorship.query.one()
    assert sponsorship.legislator_id == 1
    assert sponsorship.bill_id == 1
    assert sponsorship.added_at == datetime(2000, 1, 1, tzinfo=timezone.utc)


@responses.activate
@freeze_time("2021-1-1")
def test_update_sponsorships__remove_sponsorship():
    bill = Bill(
        id=1,
        file="Intro 200",
        name="Electric school buses",
        title="Bill title",
        status="Committee",
        intro_date="2000-1-1",
    )
    db.session.add(bill)
    legislator = Legislator(id=1, name="Patrick")
    db.session.add(legislator)

    sponsorship = BillSponsorship(
        bill_id=1,
        legislator_id=1,
        added_at=datetime(2000, 1, 1, tzinfo=timezone.utc),
    )
    db.session.add(sponsorship)

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters/1/sponsors?token=fake_token",
        json=[],
    )

    update_all_sponsorships()

    assert BillSponsorship.query.count() == 0
