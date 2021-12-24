from src import app
from src.bill.models import Bill
from src.models import BillAttachment, db
from src.utils import now

from .utils import assert_response


def test_get_bill_attachments(client):
    bill = Bill(
        id=1, name="name", file="file", title="title", intro_date=now()
    )
    attachment = BillAttachment(
        id=123, name="power hour tracker", url="http://sheets.google.com/123"
    )
    bill.attachments.append(attachment)
    db.session.add(bill)
    db.session.commit()

    response = client.get("/api/saved-bills/1/attachments")
    assert_response(
        response,
        200,
        [
            {
                "billId": 1,
                "id": 123,
                "name": "power hour tracker",
                "url": "http://sheets.google.com/123",
            }
        ],
    )


def test_add_bill_attachments(client):
    bill = Bill(
        id=1, name="name", file="file", title="title", intro_date=now()
    )
    db.session.add(bill)
    db.session.commit()

    response = client.post(
        "/api/saved-bills/1/attachments",
        data={
            "name": "power hour tracker",
            "url": "http://sheets.google.com/123",
        },
    )
    assert response.status_code == 200

    attachment = BillAttachment.query.one()
    assert attachment.name == "power hour tracker"
    assert attachment.url == "http://sheets.google.com/123"


def test_delete_bill_attachment(client):
    bill = Bill(
        id=1, name="name", file="file", title="title", intro_date=now()
    )
    attachment = BillAttachment(
        id=123, name="power hour tracker", url="http://sheets.google.com/123"
    )
    bill.attachments.append(attachment)
    db.session.add(bill)
    db.session.commit()

    client.delete("/api/saved-bills/-/attachments/123")

    attachments = BillAttachment.query.all()
    assert len(attachments) == 0
