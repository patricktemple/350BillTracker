from uuid import uuid4

from src.bill.models import Bill, CityBill
from src.models import db
from src.person.models import CouncilMember, Person, Senator, AssemblyMember
from src.sponsorship.models import CitySponsorship, SenateSponsorship, AssemblySponsorship
from src.utils import now

from .utils import get_response_data


def test_get_city_bill_sponsorships(client, city_bill):
    sponsor = Person(
        id=uuid4(), name="Sponsor", type=Person.PersonType.COUNCIL_MEMBER
    )
    sponsor.council_member = CouncilMember(city_council_person_id=1)
    sponsorship = CitySponsorship(
        bill_id=city_bill.id, council_member_id=sponsor.id, sponsor_sequence=0
    )
    db.session.add(sponsor)
    db.session.add(sponsorship)

    non_sponsor = Person(
        name="Non-sponsor", type=Person.PersonType.COUNCIL_MEMBER
    )
    non_sponsor.council_member = CouncilMember(city_council_person_id=2)
    db.session.add(non_sponsor)
    db.session.commit()

    response = client.get(f"/api/city-bills/{city_bill.id}/sponsorships")

    assert response.status_code == 200
    response_data = get_response_data(response)

    assert len(response_data) == 2
    assert response_data[0]["billId"] == str(city_bill.id)
    assert response_data[0]["person"]["name"] == "Sponsor"
    assert response_data[0]["isSponsor"] == True

    assert response_data[1]["billId"] == str(city_bill.id)
    assert response_data[1]["person"]["name"] == "Non-sponsor"
    assert response_data[1]["isSponsor"] == False


def test_get_state_bill_sponsorships(client, state_bill, city_bill, snapshot, get_uuid):
    # Ugh I should really have other decoy data in there as well to make sure it's not returned...
    senate_non_sponsor = Person(id=get_uuid(),
        name="Senate non sponsor", type=Person.PersonType.SENATOR
    )
    senate_non_sponsor.senator = Senator(state_member_id=5)
    db.session.add(senate_non_sponsor)

    senate_sponsor = Person(id=get_uuid(),
        name="Senate sponsor", type=Person.PersonType.SENATOR
    )
    senate_sponsor.senator = Senator(state_member_id=2)
    db.session.add(senate_sponsor)

    assembly_non_sponsor = Person(id=get_uuid(),
        name="Assembly non sponsor", type=Person.PersonType.ASSEMBLY_MEMBER
    )
    assembly_non_sponsor.assembly_member = AssemblyMember(state_member_id=50)
    db.session.add(assembly_non_sponsor)

    assembly_sponsor = Person(id=get_uuid(),
        name="Assembly sponsor", type=Person.PersonType.ASSEMBLY_MEMBER
    )
    assembly_sponsor.assembly_member = AssemblyMember(state_member_id=1)
    db.session.add(assembly_sponsor)

    senate_sponsorship = SenateSponsorship(senate_bill_id=state_bill.id, senator_id=senate_sponsor.id)
    db.session.add(senate_sponsorship)

    assembly_sponsorship = AssemblySponsorship(assembly_bill_id=state_bill.id, assembly_member_id=assembly_sponsor.id)
    db.session.add(assembly_sponsorship)

    db.session.commit()

    response = client.get(f"/api/state-bills/{state_bill.id}/sponsorships")

    assert response.status_code == 200
    response_data = get_response_data(response)

    assert response_data == snapshot