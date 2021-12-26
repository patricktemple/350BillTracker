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
from src.person.models import Person, CouncilMember
from src.models import db
from src.sponsorship.models import CitySponsorship
from src.static_data import COUNCIL_DATA_BY_LEGISLATOR_ID


@responses.activate
@freeze_time("2021-10-12")
def test_add_council_members():
    existing_person = Person(
        name="Corey Johnson", type=Person.PersonType.COUNCIL_MEMBER
    )
    existing_person.council_member = CouncilMember(term_start="2000-01-01", city_council_person_id=1)
    db.session.add(existing_person)

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

    assert Person.query.count() == 2
    assert CouncilMember.query.count() == 2

    corey_johnson = CouncilMember.query.filter_by(city_council_person_id=1).one()
    assert corey_johnson.person.name == "Corey Johnson the 2nd"
    assert corey_johnson.term_start == datetime(
        2021, 1, 1, tzinfo=timezone.utc
    )
    assert corey_johnson.term_end == datetime(2022, 1, 1, tzinfo=timezone.utc)

    brad_lander = CouncilMember.query.filter_by(city_council_person_id=2).one()
    assert brad_lander.person.name == "Brad Lander"


@responses.activate
def test_fill_council_person_data():
    person_to_update = Person(name="Corey Johnson", type=Person.PersonType.COUNCIL_MEMBER)
    person_to_update.council_member = CouncilMember(city_council_person_id=1)
    db.session.add(person_to_update)

    person_without_new_data = Person(
        name="Person who was impeached and removed", type=Person.PersonType.COUNCIL_MEMBER
    )
    person_without_new_data.council_member = CouncilMember(city_council_person_id=2)
    db.session.add(person_without_new_data)

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

    assert Person.query.count() == 2
    assert CouncilMember.query.count() == 2

    corey = CouncilMember.query.filter_by(city_council_person_id=1).one()
    assert corey.person.email == "corey@council.nyc.gov"
    assert corey.person.phone == "555-111-1111"
    assert corey.legislative_phone == "888-888-8888"
    assert corey.website == "https://www.example.com/"


def test_fill_council_person_static_data():
    corey_static = COUNCIL_DATA_BY_LEGISLATOR_ID[7631]
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
