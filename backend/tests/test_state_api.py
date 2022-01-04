from src.state_api import add_state_representatives
from unittest.mock import patch

import responses

from .utils import get_response_data

@responses.activate
def test_import_state_reps(client, senator, assembly_member, snapshot):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/members/2021?limit=1000&full=true&key=fake_key",
        json={
            "result": {"items": [
                {
                    "memberId": 1,
                    "chamber": "SENATE",
                    "person": {
                        "fullName": "New senator",
                        "prefix": "Senator",
                        "email": "a@example.com"
                    }
                },
                {
                    "memberId": senator.senator.state_member_id,
                    "chamber": "SENATE",
                    "person": {
                        "fullName": "Existing senator",
                        "prefix": "Senator",
                        "email": "b@example.com"
                    }
                },
                {
                    "memberId": 1,
                    "chamber": "ASSEMBLY",
                    "person": {
                        "fullName": "New assembly member",
                        "prefix": "Assembly member",
                        "email": "c@example.com"
                    }
                },
                {
                    "memberId": assembly_member.assembly_member.state_member_id,
                    "chamber": "ASSEMBLY",
                    "person": {
                        "fullName": "Existing assembly member",
                        "prefix": "Assembly",
                        "email": "d@example.com"
                    }
                },
            ]
        }}
    )
    add_state_representatives()

    response = client.get("/api/persons")

    # Get rid of random UUIDs for snapshot
    response_data = get_response_data(response)
    for item in response_data:
        del item['id']
    
    assert response_data == snapshot