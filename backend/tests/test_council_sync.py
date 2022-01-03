from datetime import datetime, timezone
from uuid import uuid4

import responses
from freezegun import freeze_time

from src.bill.models import Bill, CityBill
from src.council_sync import (add_council_members,
                              fill_council_person_data_from_api,
                              fill_council_person_static_data,
                              sync_bill_updates, update_all_sponsorships)
from src.models import db
from src.person.models import CouncilMember, Person
from src.sponsorship.models import CitySponsorship
from src.static_data import COUNCIL_DATA_BY_LEGISLATOR_ID


@responses.activate
@freeze_time("2021-10-12")
def test_add_council_members():
    existing_person = Person(
        name="Corey Johnson", type=Person.PersonType.COUNCIL_MEMBER
    )
    existing_person.council_member = CouncilMember(
        term_start="2000-01-01", city_council_person_id=1
    )
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

    corey_johnson = CouncilMember.query.filter_by(
        city_council_person_id=1
    ).one()
    assert corey_johnson.person.name == "Corey Johnson the 2nd"
    assert corey_johnson.term_start == datetime(
        2021, 1, 1, tzinfo=timezone.utc
    )
    assert corey_johnson.term_end == datetime(2022, 1, 1, tzinfo=timezone.utc)

    brad_lander = CouncilMember.query.filter_by(city_council_person_id=2).one()
    assert brad_lander.person.name == "Brad Lander"


@responses.activate
def test_fill_council_person_data():
    person_to_update = Person(
        name="Corey Johnson", type=Person.PersonType.COUNCIL_MEMBER
    )
    person_to_update.council_member = CouncilMember(city_council_person_id=1)
    db.session.add(person_to_update)

    person_without_new_data = Person(
        name="Person who was impeached and removed",
        type=Person.PersonType.COUNCIL_MEMBER,
    )
    person_without_new_data.council_member = CouncilMember(
        city_council_person_id=2
    )
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
    person_to_update = Person(
        name="Corey Johnson badly formatted name----",
        email="existing-email@council.nyc.gov",
        type=Person.PersonType.COUNCIL_MEMBER,
    )
    person_to_update.council_member = CouncilMember(
        city_council_person_id=7631
    )
    db.session.add(person_to_update)

    person_without_static_data = Person(
        name="Person without static data",
        type=Person.PersonType.COUNCIL_MEMBER,
    )
    person_without_static_data.council_member = CouncilMember(
        city_council_person_id=2,
    )
    db.session.add(person_without_static_data)

    fill_council_person_static_data()

    corey = CouncilMember.query.filter_by(city_council_person_id=7631).one()

    assert corey.person.name == corey_static["name"]
    assert corey.person.twitter == corey_static["twitter"]
    assert corey.person.party == corey_static["party"]
    assert corey.borough == corey_static["borough"]
    assert corey.person.email == "existing-email@council.nyc.gov"


@responses.activate
def test_sync_bill_updates(bill):
    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/matters/1?token=fake_token",
        json={
            "MatterId": bill.city_bill.city_bill_id,
            "MatterFile": "New file",
            "MatterName": "New name",
            "MatterTitle": "New title",
            "MatterBodyName": "New body",
            "MatterIntroDate": "2021-01-01T00:00:00",
            "MatterStatusName": "New status",
            "MatterVersion": "New version",
        },
    )

    sync_bill_updates()

    result = Bill.query.one()
    assert result.name == "New name"
    assert result.description == "New title"
    assert result.city_bill.file == "New file"
    assert result.city_bill.council_body == "New body"
    assert result.city_bill.status == "New status"
    assert result.city_bill.intro_date == datetime(
        2021, 1, 1, tzinfo=timezone.utc
    )
    assert result.nickname == bill.nickname
    assert result.city_bill.active_version == "New version"


@responses.activate
@freeze_time("2021-1-1")
def test_update_sponsorships__new_sponsor(bill):
    person = Person(name="Patrick", type=Person.PersonType.COUNCIL_MEMBER)
    person.council_member = CouncilMember(city_council_person_id=1)
    db.session.add(person)

    wrong_version_person = Person(
        name="Jim", type=Person.PersonType.COUNCIL_MEMBER
    )
    wrong_version_person.council_member = CouncilMember(
        city_council_person_id=2
    )
    db.session.add(wrong_version_person)

    responses.add(
        responses.GET,
        url=f"https://webapi.legistar.com/v1/nyc/matters/{bill.city_bill.city_bill_id}/sponsors?token=fake_token",
        json=[
            {
                "MatterSponsorNameId": 1,
                "MatterSponsorSequence": 0,
                "MatterSponsorMatterVersion": "A",
            },
            {
                # This one isn't found in the DB
                "MatterSponsorNameId": 3,
                "MatterSponsorSequence": 1,
                "MatterSponsorMatterVersion": "A",
            },
            {
                "MatterSponsorNameId": 2,
                "MatterSponsorSequence": 0,
                "MatterSponsorMatterVersion": "different",
            },
        ],
    )

    update_all_sponsorships()

    sponsorship = CitySponsorship.query.one()
    assert sponsorship.council_member_id == person.id
    assert sponsorship.bill_id == bill.id
    assert sponsorship.added_at == datetime(2021, 1, 1, tzinfo=timezone.utc)


@responses.activate
@freeze_time("2021-1-1")
def test_update_sponsorships__sponsorship_already_exists(bill):
    person = Person(
        id=uuid4(), name="Patrick", type=Person.PersonType.COUNCIL_MEMBER
    )
    person.council_member = CouncilMember(city_council_person_id=1)
    db.session.add(person)

    sponsorship = CitySponsorship(
        bill_id=bill.id,
        council_member_id=person.id,
        added_at=datetime(2000, 1, 1, tzinfo=timezone.utc),
        sponsor_sequence=0,
    )
    db.session.add(sponsorship)

    responses.add(
        responses.GET,
        url=f"https://webapi.legistar.com/v1/nyc/matters/{bill.city_bill.city_bill_id}/sponsors?token=fake_token",
        json=[
            {
                "MatterSponsorNameId": 1,
                "MatterSponsorSequence": 0,
                "MatterSponsorMatterVersion": "A",
            }
        ],
    )

    update_all_sponsorships()

    sponsorship = CitySponsorship.query.one()
    assert sponsorship.council_member_id == person.id
    assert sponsorship.bill_id == bill.id
    assert sponsorship.added_at == datetime(2000, 1, 1, tzinfo=timezone.utc)


@responses.activate
@freeze_time("2021-1-1")
def test_update_sponsorships__remove_sponsorship(bill):
    person = Person(
        id=uuid4(), name="Patrick", type=Person.PersonType.COUNCIL_MEMBER
    )
    person.council_member = CouncilMember(city_council_person_id=1)
    db.session.add(person)

    sponsorship = CitySponsorship(
        bill_id=bill.id,
        council_member_id=person.id,
        added_at=datetime(2000, 1, 1, tzinfo=timezone.utc),
        sponsor_sequence=0,
    )
    db.session.add(sponsorship)

    responses.add(
        responses.GET,
        url=f"https://webapi.legistar.com/v1/nyc/matters/{bill.city_bill.city_bill_id}/sponsors?token=fake_token",
        json=[],
    )

    update_all_sponsorships()

    assert CitySponsorship.query.count() == 0
