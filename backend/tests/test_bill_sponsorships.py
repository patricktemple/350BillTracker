from src import app
from src.bill.models import Bill
from src.models import BillSponsorship, Legislator, db
from src.utils import now

from .utils import get_response_data


def test_get_bill_sponsorships(client):
    bill = Bill(
        id=1, name="name", file="file", title="title", intro_date=now()
    )
    db.session.add(bill)

    sponsor = Legislator(id=1, name="Sponsor")
    sponsorship = BillSponsorship(bill_id=1, legislator_id=1)
    db.session.add(sponsor)
    db.session.add(sponsorship)

    non_sponsor = Legislator(id=2, name="Non-sponsor")
    db.session.add(non_sponsor)
    db.session.commit()

    response = client.get("/api/saved-bills/1/sponsorships")

    assert response.status_code == 200
    response_data = get_response_data(response)

    assert len(response_data) == 2
    assert response_data[0]["billId"] == 1
    assert response_data[0]["legislator"]["name"] == "Sponsor"
    assert response_data[0]["isSponsor"] == True

    assert response_data[1]["billId"] == 1
    assert response_data[1]["legislator"]["name"] == "Non-sponsor"
    assert response_data[1]["isSponsor"] == False
