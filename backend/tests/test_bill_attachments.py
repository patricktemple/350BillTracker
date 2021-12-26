from uuid import uuid4

from src.bill.models import BillAttachment
from src.models import db

from .utils import assert_response


def test_get_bill_attachments(client, bill):
    attachment = BillAttachment(
        id=uuid4(),
        name="power hour tracker",
        url="http://sheets.google.com/123",
    )
    bill.attachments.append(attachment)
    db.session.commit()

    response = client.get(f"/api/saved-bills/{bill.id}/attachments")
    assert_response(
        response,
        200,
        [
            {
                "billId": str(bill.id),
                "id": str(attachment.id),
                "name": "power hour tracker",
                "url": "http://sheets.google.com/123",
            }
        ],
    )


def test_add_bill_attachments(client, bill):
    response = client.post(
        f"/api/saved-bills/{bill.id}/attachments",
        data={
            "name": "power hour tracker",
            "url": "http://sheets.google.com/123",
        },
    )
    assert response.status_code == 200

    attachment = BillAttachment.query.one()
    assert attachment.name == "power hour tracker"
    assert attachment.url == "http://sheets.google.com/123"


def test_delete_bill_attachment(client, bill):
    attachment = BillAttachment(
        id=uuid4(),
        name="power hour tracker",
        url="http://sheets.google.com/123",
    )
    bill.attachments.append(attachment)
    db.session.commit()

    client.delete(f"/api/saved-bills/-/attachments/{attachment.id}")

    attachments = BillAttachment.query.all()
    assert len(attachments) == 0
