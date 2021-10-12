from src.models import Legislator, db
from src.council_sync import add_council_members
import responses
from freezegun import freeze_time
from datetime import datetime, timezone

@responses.activate
@freeze_time("2021-10-12")
def test_add_council_members():
    existing_legislator = Legislator(id=1, name="Corey Johnson", term_start="2000-01-01")
    db.session.add(existing_legislator)

    responses.add(
        responses.GET,
        url="https://webapi.legistar.com/v1/nyc/officerecords?token=fake_token&%24filter=OfficeRecordBodyName+eq+%27City+Council%27+and+OfficeRecordStartDate+le+datetime%272021-10-12%27+and+OfficeRecordEndDate+ge+datetime%272021-10-12%27",
        json=[{
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
        }]
    )

    add_council_members()

    assert Legislator.query.count() == 2

    corey_johnson = Legislator.query.get(1)
    assert corey_johnson.name == "Corey Johnson the 2nd"
    assert corey_johnson.term_start == datetime(2021, 1, 1, tzinfo=timezone.utc)
    assert corey_johnson.term_end == datetime(2022, 1, 1, tzinfo=timezone.utc)

    brad_lander = Legislator.query.get(2)
    assert brad_lander.name == "Brad Lander"
