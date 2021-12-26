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


@fixture
def staffer_person(council_member_person):
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
    return staffer_person


def test_get_person_staffers(client, council_member_person, staffer_person):
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


def test_add_legislator_staffer(client, council_member_person):
    response = client.post(
        f"/api/persons/{council_member_person.id}/staffers",
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
    assert staffer.person.name == "staffer"
    assert staffer.person.title == "chief of staff"
    assert staffer.person.twitter == "TheChief"
    assert staffer.person.phone == "111-111-1111"
    assert staffer.person.email == "test@example.com"
    assert staffer.boss_id == council_member_person.id


def test_add_legislator_invalid_twitter(client, council_member_person):
    response = client.post(
        f"/api/persons/{council_member_person.id}/staffers",
        data={
            "name": "staffer",
            "twitter": "&@89)(",
        },
    )
    assert response.status_code == 422


def test_delete_staffer(client, council_member_person, staffer_person):
    client.delete(f"/api/persons/-/staffers/{staffer_person.id}")

    staffers = Staffer.query.all()
    assert len(staffers) == 0
