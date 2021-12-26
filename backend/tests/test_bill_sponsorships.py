from uuid import uuid4

from src.bill.models import Bill, CityBill
from src.models import db
from src.person.models import CouncilMember, Person
from src.sponsorship.models import CitySponsorship
from src.utils import now

from .utils import get_response_data


def test_get_bill_sponsorships(client):
    bill = Bill(id=uuid4(), name="name", type=Bill.BillType.CITY)
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        title="title",
        status="Enacted",
        intro_date=now(),
        active_version="A",
    )
    db.session.add(bill)

    sponsor = Person(
        id=uuid4(), name="Sponsor", type=Person.PersonType.COUNCIL_MEMBER
    )
    sponsor.council_member = CouncilMember(city_council_person_id=1)
    sponsorship = CitySponsorship(
        bill_id=bill.id, council_member_id=sponsor.id, sponsor_sequence=0
    )
    db.session.add(sponsor)
    db.session.add(sponsorship)

    non_sponsor = Person(
        name="Non-sponsor", type=Person.PersonType.COUNCIL_MEMBER
    )
    non_sponsor.council_member = CouncilMember(city_council_person_id=2)
    db.session.add(non_sponsor)
    db.session.commit()

    response = client.get(f"/api/city-bills/{bill.id}/sponsorships")

    assert response.status_code == 200
    response_data = get_response_data(response)

    assert len(response_data) == 2
    assert response_data[0]["billId"] == str(bill.id)
    assert response_data[0]["person"]["name"] == "Sponsor"
    assert response_data[0]["isSponsor"] == True

    assert response_data[1]["billId"] == str(bill.id)
    assert response_data[1]["person"]["name"] == "Non-sponsor"
    assert response_data[1]["isSponsor"] == False
