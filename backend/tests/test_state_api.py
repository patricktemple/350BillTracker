from unittest.mock import patch

import responses

from src.state_api import add_state_representatives

from .utils import get_response_data, create_mock_bill_response


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
                    {
                        "memberId": 5,
                        "chamber": "ASSEMBLY",
                        "districtCode": 5,
                        "incumbent": False,
                        "person": {
                            "fullName": "New member out of office",
                            "prefix": "Assembly",
                            "email": "d@example.com",
                        },
                    },
                ]
            }
        },
    )
    add_state_representatives()

    response = client.get("/api/persons")

    # Get rid of random UUIDs for snapshot
    response_data = get_response_data(response)
    for item in response_data:
        del item["id"]

    assert response_data == snapshot


@responses.activate
def test_update_state_bills(state_bill):
    # TODO work on this... need to plan it out
    responses.add(
        responses.GET,
        url=f"https://legislation.nysenate.gov/api/3/bills/{state_bill.session_year}/{state_bill.senate_bill.base_print_no}?view=no_fulltext&key=fake_key",
        json=create_mock_bill_response(
            base_print_no=state_bill.senate_bill.base_print_no,
            chamber="SENATE",
            cosponsor_member_id=2,
            lead_sponsor_member_id=4,
        ),