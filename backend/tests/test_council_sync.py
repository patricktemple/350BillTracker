from datetime import datetime, timezone

import responses
from freezegun import freeze_time

from src.council_sync import (
    add_council_members,
    fill_council_person_data_from_api,
    fill_council_person_static_data,
)
from src.models import Legislator, db


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
    assert corey.borough == "Manhattan"
    assert corey.website == "https://www.example.com/"


def test_fill_council_person_static_data():
    legislator_to_update = Legislator(
        id=7631, name="Corey Johnson badly formatted name----"
    )
    db.session.add(legislator_to_update)

    legislator_without_static_data = Legislator(
        id=2, name="Person without static data"
    )
    db.session.add(legislator_without_static_data)

    fill_council_person_static_data()

    corey = Legislator.query.get(7631)
    assert corey.name == "Corey D. Johnson"
    assert corey.twitter == "NYCSpeakerCoJo"
    assert corey.party == "D"
