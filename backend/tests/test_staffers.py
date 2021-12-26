from uuid import uuid4

from pytest import fixture

from src import app
from src.models import db
from src.person.models import CouncilMember, Person, Staffer

from .utils import assert_response


@fixture
def council_member_person():
    person = Person(
        id=uuid4(), name="Person name", type=Person.PersonType.COUNCIL_MEMBER
    )
    person.council_member = CouncilMember(city_council_person_id=1)
    db.session.add(person)
    db.session.commit()
    return person


def test_get_person_staffers(client, council_member_person):
    staffer_person = Person(
        id=uuid4(),
        name="Staffer name",
        title="chief of staff",
        email="test@example.com",
        twitter="TheChief",
        phone="111-111-1111",
        type=Person.PersonType.STAFFER,
    )
    staffer_person.staffer = Staffer(boss_id=council_member_person.id)
    db.session.add(staffer_person)
    db.session.commit()

    response = client.get(f"/api/persons/{council_member_person.id}/staffers")
    assert_response(
        response,
        200,
        [
            {
                "assemblyMember": None,
                "councilMember": None,
                "email": "test@example.com",
                "id": str(staffer_person.id),
                "name": "Staffer name",
                "notes": None,
                "party": None,
                "phone": "111-111-1111",
                "senator": None,
                "title": "chief of staff",
                "twitter": "TheChief",
                "type": "STAFFER",
            }
        ],
    )


def test_add_legislator_staffer(client):
    legislator = Legislator(id=1, name="name")
    db.session.add(legislator)
    db.session.commit()

    response = client.post(
        "/api/legislators/1/staffers",
        data={
            "name": "staffer",
            "title": "chief of staff",
            "twitter": "TheChief",
            "phone": "111-111-1111",
            "email": "test@example.com",
        },
    )
    assert response.status_code == 200

    staffer = Staffer.query.one()
    assert staffer.name == "staffer"
    assert staffer.title == "chief of staff"
    assert staffer.twitter == "TheChief"
    assert staffer.phone == "111-111-1111"
    assert staffer.email == "test@example.com"


def test_add_legislator_invalid_twitter(client):
    legislator = Legislator(id=1, name="name")
    db.session.add(legislator)
    db.session.commit()

    response = client.post(
        "/api/legislators/1/staffers",
        data={
            "name": "staffer",
            "twitter": "&@89)(",
        },
    )
    assert response.status_code == 422


def test_delete_bill_attachment(client):
    staffer_id = uuid4()
    legislator = Legislator(id=1, name="name")
    staffer = Staffer(
        id=staffer_id,
        name="staffer",
    )
    legislator.staffers.append(staffer)
    db.session.add(legislator)
    db.session.commit()

    client.delete(f"/api/legislators/-/staffers/{staffer_id}")

    staffers = Staffer.query.all()
    assert len(staffers) == 0
