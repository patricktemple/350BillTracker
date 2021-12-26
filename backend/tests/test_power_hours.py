from unittest.mock import patch
from uuid import uuid4

from pytest import fixture

from src import app
from src.bill.models import Bill, CityBill, PowerHour
from src.models import db
from src.utils import now

from .utils import get_response_data


# TODO consider sharing this fixture w/ test_bill_attachments
@fixture
def bill():
    bill = Bill(id=uuid4(), name="name", type=Bill.BillType.CITY)
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        title="title",
        intro_date=now(),
        status="Enacted",
        active_version="A"
    )
    db.session.add(bill)
    return bill


def test_get_power_hours(client, bill):
    power_hour = PowerHour(
        bill_id=bill.id,
        spreadsheet_id="123",
        spreadsheet_url="https://sheets.google.com/123",
        title="My power hour",
        created_at="2021-01-01T00:00:00+00:00",
    )
    db.session.add(power_hour)

    db.session.commit()

    response = client.get(f"/api/saved-bills/{bill.id}/power-hours")

    assert response.status_code == 200
    response_data = get_response_data(response)

    assert len(response_data) == 1
    assert (
        response_data[0]["spreadsheetUrl"] == "https://sheets.google.com/123"
    )
    assert response_data[0]["title"] == "My power hour"
    assert response_data[0]["createdAt"] == "2021-01-01T00:00:00+00:00"


@patch("src.bill.views.create_power_hour")
def test_create_power_hour__no_import(mock_create_power_hour, client, bill):
    mock_create_power_hour.return_value = (
        {"spreadsheetId": 1, "spreadsheetUrl": "http://example.com"},
        ["Power hour created"],
    )

    response = client.post(
        f"/api/saved-bills/{bill.id}/power-hours",
        data={"title": "My power hour"},
    )

    assert response.status_code == 200
    response_data = get_response_data(response)
    assert response_data["powerHour"]["title"] == "My power hour"
    assert response_data["messages"] == ["Power hour created"]

    power_hour = PowerHour.query.one()
    assert power_hour.spreadsheet_url == "http://example.com"
    assert power_hour.spreadsheet_id == "1"


@patch("src.bill.views.create_power_hour")
def test_create_power_hour__with_import(mock_create_power_hour, client, bill):
    power_hour = PowerHour(
        bill_id=bill.id,
        spreadsheet_id="123",
        spreadsheet_url="https://sheets.google.com/123",
        title="Old power hour",
        created_at="2021-01-01T00:00:00+00:00",
    )
    db.session.add(power_hour)

    db.session.commit()

    mock_create_power_hour.return_value = (
        {"spreadsheetId": 1, "spreadsheetUrl": "http://example.com"},
        ["Power hour created"],
    )
    response = client.post(
        f"/api/saved-bills/{bill.id}/power-hours",
        data={
            "title": "My power hour",
            "powerHourIdToImport": str(power_hour.id),
        },
    )

    assert response.status_code == 200
    mock_create_power_hour.assert_called_with(bill.id, "My power hour", "123")
