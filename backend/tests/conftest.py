from uuid import UUID, uuid4

import pytest

from src import app, models
from src.bill.models import (
    AssemblyBill,
    Bill,
    CityBill,
    SenateBill,
    StateBill,
    db,
)
from src.person.models import (
    AssemblyMember,
    CouncilMember,
    OfficeContact,
    Person,
    Senator,
    Staffer,
)
from src.user.models import User
from src.utils import now

from .utils import ApiClient


@pytest.fixture(autouse=True)
def autouse_fixtures():
    models.db.drop_all()
    models.db.create_all()

    yield

    models.db.session.close()


# TODO: Do we want this?
# @pytest.fixture(autouse=True)
# def request_context(app):
#     with app.test_request_context():
#         yield


@pytest.fixture
def get_uuid():
    count = 0

    def impl():
        nonlocal count
        count += 1
        return UUID(int=count)

    return impl


@pytest.fixture
def city_bill():
    bill = Bill(
        id=uuid4(),
        name="name",
        description="description",
        nickname="nickname",
        type=Bill.BillType.CITY,
    )
    bill.city_bill = CityBill(
        city_bill_id=1,
        file="file",
        intro_date=now(),
        status="Enacted",
        active_version="A",
    )
    db.session.add(bill)
    db.session.commit()
    return bill


@pytest.fixture
def council_member(get_uuid):
    person = Person(
        id=get_uuid(),
        type=Person.PersonType.COUNCIL_MEMBER,
        name="council member name",
        title="Council member",
        email="me@example.com",
        twitter="pmtemple",
        party="D",
    )
    person.office_contacts.append(
        OfficeContact(
            phone="111-222-3333",
            type=OfficeContact.OfficeContactType.CENTRAL_OFFICE,
        )
    )
    person.council_member = CouncilMember(
        city_council_person_id=50,
        borough="Bronx",
        website="http://council.nyc.gov",
    )
    db.session.add(person)
    db.session.commit()
    return person


@pytest.fixture
def senator(get_uuid):
    person = Person(
        id=get_uuid(),
        type=Person.PersonType.SENATOR,
        name="senator name",
        title="Senator",
        email="me@senate.com",
        twitter="thesenateguy",
        party="D",
    )
    person.office_contacts.append(
        OfficeContact(
            phone="111-222-3333",
            fax="888-888-8888",
            city="Albany",
            type=OfficeContact.OfficeContactType.CENTRAL_OFFICE,
        )
    )
    person.senator = Senator(state_member_id=50, district=3)
    db.session.add(person)
    db.session.commit()
    return person


@pytest.fixture
def senate_staffer(senator, get_uuid):
    person = Person(
        id=get_uuid(),
        type=Person.PersonType.STAFFER,
        name="staffer name",
        title="Chief of staffer",
        email="me@staff.com",
        twitter="thestaff",
        party="D",
    )
    person.office_contacts.append(
        OfficeContact(
            phone="111-222-3333", type=OfficeContact.OfficeContactType.OTHER
        )
    )
    person.staffer = Staffer(boss_id=senator.id)
    db.session.add(person)
    db.session.commit()
    return person


@pytest.fixture
def assembly_member(get_uuid):
    person = Person(
        id=get_uuid(),
        type=Person.PersonType.ASSEMBLY_MEMBER,
        name="assemblymember name",
        title="Assemblymember",
        email="me@assembly.com",
        # phone="1-555-555-5555",
        twitter="theassembly",
        party="D",
    )
    person.office_contacts.append(
        OfficeContact(
            phone="111-222-3333",
            type=OfficeContact.OfficeContactType.CENTRAL_OFFICE,
        )
    )
    person.assembly_member = AssemblyMember(state_member_id=51, district=5)
    db.session.add(person)
    db.session.commit()
    return person


@pytest.fixture
def state_bill(get_uuid):
    bill = Bill(
        id=get_uuid(),
        name="state bill",
        description="description",
        nickname="nickname",
        type=Bill.BillType.STATE,
    )
    bill.state_bill = StateBill(
        session_year=2021,
    )
    bill.state_bill.senate_bill = SenateBill(
        base_print_no="S1234", active_version="", status="Committee"
    )
    bill.state_bill.assembly_bill = AssemblyBill(
        base_print_no="A1234", active_version="A", status="Voted"
    )
    db.session.add(bill)
    db.session.commit()
    return bill


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def user_email():
    return "test@example.com"


@pytest.fixture
def user_name():
    return "Test user"


@pytest.fixture
def client(user_id, user_email, user_name):
    app.app.test_client_class = ApiClient
    with app.app.test_client() as client:
        user = User(id=user_id, name=user_name, email=user_email)
        models.db.session.add(user)
        models.db.session.commit()

        client.set_authenticated_user_id(user_id)
        yield client


@pytest.fixture
def unauthenticated_client():
    app.app.test_client_class = ApiClient
    with app.app.test_client() as client:
        yield client
