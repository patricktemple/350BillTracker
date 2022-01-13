import pytest
import responses

from src.app import app
from src.bill.models import Bill
from src.models import db
from src.person.models import AssemblyMember, Person, Senator
from src.person.schema import PersonWithContactsSchema
from src.sponsorship.models import AssemblySponsorship, SenateSponsorship
from src.state_api import sync_state_representatives, update_state_bills

from .utils import create_mock_bill_response, get_response_data


@responses.activate
def test_import_state_reps(client, senator, assembly_member, snapshot):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/members/2021?limit=1000&full=true&key=fake_key",
        json={
            "result": {
                "items": [
                    {
                        "memberId": 1,
                        "chamber": "SENATE",
                        "districtCode": 1,
                        "incumbent": True,
                        "person": {
                            "fullName": "New senator",
                            "prefix": "Senator",
                            "email": "a@example.com",
                        },
                    },
                    {
                        "memberId": senator.senator.state_member_id,
                        "chamber": "SENATE",
                        "districtCode": 2,
                        "incumbent": True,
                        "person": {
                            "fullName": "Existing senator",
                            "prefix": "Senator",
                            "email": "b@example.com",
                        },
                    },
                    {
                        "memberId": 1,
                        "chamber": "ASSEMBLY",
                        "districtCode": 3,
                        "incumbent": True,
                        "person": {
                            "fullName": "New assembly member",
                            "prefix": "Assembly member",
                            "email": "c@example.com",
                        },
                    },
                    {
                        "memberId": assembly_member.assembly_member.state_member_id,
                        "chamber": "ASSEMBLY",
                        "districtCode": 4,
                        "incumbent": True,
                        "person": {
                            "fullName": "Existing assembly member",
                            "prefix": "Assembly",
                            "email": "d@example.com",
                        },
                    },
                ]
            }
        },
    )
    sync_state_representatives()

    persons = Person.query.all()
    

    # Get rid of random UUIDs for snapshot
    with app.app_context():
        # Super lazy way to run a snapshot on the full payload:
        item_json = PersonWithContactsSchema(many=True).dump(persons)
    for item in item_json:
        del item["id"]

    assert item_json == snapshot


@responses.activate
def test_import_state_reps__district_conflict_checks_incumbent(client):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/members/2021?limit=1000&full=true&key=fake_key",
        json={
            "result": {
                "items": [
                    {
                        "memberId": 1,
                        "chamber": "SENATE",
                        "districtCode": 1,
                        "incumbent": True,
                        "person": {
                            "fullName": "Incumbent senator",
                            "prefix": "Senator",
                            "email": "a@example.com",
                        },
                    },
                    {
                        "memberId": 2,
                        "chamber": "SENATE",
                        "districtCode": 1,
                        "incumbent": False,
                        "person": {
                            "fullName": "Non-incumbent senator",
                            "prefix": "Senator",
                            "email": "b@example.com",
                        },
                    },
                ]
            }
        },
    )
    sync_state_representatives()

    response = client.get("/api/persons")

    response_data = get_response_data(response)

    assert len(response_data) == 1
    assert response_data[0]["name"] == "Incumbent senator"


@responses.activate
@pytest.mark.parametrize("incumbent", [False, True])
def test_import_state_reps__district_no_single_incumbent(client, incumbent):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/members/2021?limit=1000&full=true&key=fake_key",
        json={
            "result": {
                "items": [
                    {
                        "memberId": 1,
                        "chamber": "SENATE",
                        "districtCode": 1,
                        "incumbent": incumbent,
                        "person": {
                            "fullName": "Non-incumbent senator",
                            "prefix": "Senator",
                            "email": "a@example.com",
                        },
                    },
                    {
                        "memberId": 2,
                        "chamber": "SENATE",
                        "districtCode": 1,
                        "incumbent": incumbent,
                        "person": {
                            "fullName": "Non-incumbent senator",
                            "prefix": "Senator",
                            "email": "b@example.com",
                        },
                    },
                ]
            }
        },
    )
    sync_state_representatives()

    response = client.get("/api/persons")

    assert not get_response_data(response)


@responses.activate
def test_update_state_bills(state_bill: Bill, senator, assembly_member):
    responses.add(
        responses.GET,
        url=f"https://legislation.nysenate.gov/api/3/bills/{state_bill.state_bill.session_year}/{state_bill.state_bill.senate_bill.base_print_no}?view=no_fulltext&key=fake_key",
        json=create_mock_bill_response(
            base_print_no=state_bill.state_bill.senate_bill.base_print_no,
            chamber="SENATE",
            cosponsor_member_id=100,
            lead_sponsor_member_id=4,
            active_version="New senate version",
            status="New senate status",
            same_as_base_print_no=state_bill.state_bill.assembly_bill.base_print_no,
        ),
    )

    responses.add(
        responses.GET,
        url=f"https://legislation.nysenate.gov/api/3/bills/{state_bill.state_bill.session_year}/{state_bill.state_bill.assembly_bill.base_print_no}?view=no_fulltext&key=fake_key",
        json=create_mock_bill_response(
            base_print_no=state_bill.state_bill.assembly_bill.base_print_no,
            chamber="ASSEMBLY",
            cosponsor_member_id=50,
            lead_sponsor_member_id=200,
            active_version="New assembly version",
            status="New assembly status",
            same_as_base_print_no=state_bill.state_bill.senate_bill.base_print_no,
        ),
    )

    # Start with one sponsors on each chamber, and then expect it to switch to a
    # different sponsor for each chamber
    db.session.add(
        SenateSponsorship(
            person_id=senator.id, bill_id=state_bill.id, is_lead_sponsor=False
        )
    )
    db.session.add(
        AssemblySponsorship(
            person_id=assembly_member.id,
            bill_id=state_bill.id,
            is_lead_sponsor=False,
        )
    )
    db.session.commit()

    different_senate_person = Person(
        name="Different senator", type=Person.PersonType.SENATOR
    )
    different_senate_person.senator = Senator(state_member_id=100)
    db.session.add(different_senate_person)

    different_assembly_person = Person(
        name="Different assembly member",
        type=Person.PersonType.ASSEMBLY_MEMBER,
    )
    different_assembly_person.assembly_member = AssemblyMember(
        state_member_id=200
    )
    db.session.add(different_assembly_person)

    update_state_bills()

    # Ensure it committed by rolling back any uncommitted changes
    db.session.rollback()

    assert state_bill.state_bill.senate_bill.status == "New senate status"
    assert (
        state_bill.state_bill.senate_bill.active_version
        == "New senate version"
    )
    assert len(state_bill.state_bill.senate_bill.sponsorships) == 1

    senate_sponsorship = state_bill.state_bill.senate_bill.sponsorships[0]
    assert senate_sponsorship.representative.person.name == "Different senator"
    assert not senate_sponsorship.is_lead_sponsor

    assert state_bill.state_bill.assembly_bill.status == "New assembly status"
    assert (
        state_bill.state_bill.assembly_bill.active_version
        == "New assembly version"
    )
    assert len(state_bill.state_bill.assembly_bill.sponsorships) == 1

    assembly_sponsorship = state_bill.state_bill.assembly_bill.sponsorships[0]
    assert (
        assembly_sponsorship.representative.person.name
        == "Different assembly member"
    )
    assert assembly_sponsorship.is_lead_sponsor
