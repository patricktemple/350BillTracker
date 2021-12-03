from src import app
from src.models import Bill, PowerHour, db
from src.utils import now

from .utils import get_response_data


def test_get_power_hours(client):
    bill = Bill(
        id=1, name="name", file="file", title="title", intro_date=now()
    )
    db.session.add(bill)

    power_hour = PowerHour(bill_id=bill.id, spreadsheet_id="123", spreadsheet_url="https://sheets.google.com/123", title="My power hour", created_at="2021-01-01T00:00:00Z")
    db.session.add(power_hour)

    db.session.commit()

    response = client.get("/api/saved-bills/1/power-hours")

    assert response.status_code == 200
    response_data = get_response_data(response)

    print(response_data)
    assert len(response_data) == 1
    assert response_data[0]['spreadsheetUrl'] == "https://sheets.google.com/123"
    assert response_data[0]['title'] == "My power hour"

    # This is failing: wrong time zone?
    assert response_data[0]['createdAt'] == "My power hour"