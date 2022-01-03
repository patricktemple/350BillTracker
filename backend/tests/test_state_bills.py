import json
from uuid import uuid4

import responses

from src.bill.models import DEFAULT_TWITTER_SEARCH_TERMS, Bill, CityBill
from src.models import db
from src.person.models import Senator, AssemblyMember, Person
from src.utils import now

from .utils import assert_response

# TODO: Fix black formatter!!!
def test_get_bills(client, state_bill):
    response = client.get("/api/bills")
    assert_response(
        response,
        200,
[{'cityBill': None, 'codeName': 'S1234 / A1234 from 2021 session', 'description': 'description', 'id': str(state_bill.id), 'name': 'state bill', 'nickname': 'nickname', 'notes': '', 'stateBill': {'assemblyBill': {'activeVersion': 'A', 'assemblyWebsite': 'https://nyassembly.gov/leg/?term=2021&bn=A1234', 'basePrintNo': 'A1234', 'senateWebsite': 'https://www.nysenate.gov/legislation/bills/2021/A1234', 'sponsorCount': 0, 'status': 'Voted'}, 'senateBill': {'activeVersion': '', 'assemblyWebsite': 'https://nyassembly.gov/leg/?term=2021&bn=S1234', 'basePrintNo': 'S1234', 'senateWebsite': 'https://www.nysenate.gov/legislation/bills/2021/S1234', 'sponsorCount': 0, 'status': 'Committee'}}, 'status': 'Committee / Voted', 'tracked': True, 'twitterSearchTerms': ['solar', 'climate', 'wind power', 'renewable', 'fossil fuel'], 'type': 'STATE'}],
    )


def test_delete_bill(client, state_bill):
    response = client.get("/api/bills")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1

    response = client.delete(f"/api/bills/{state_bill.id}")
    assert response.status_code == 200

    response = client.get("/api/bills")
    assert_response(response, 200, [])



@responses.activate
def test_track_bill(client):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/2021/S100?view=no_fulltext&key=fake_key",
        json={"result": {
            "title": "Senate bill title",
            "summary": "Senate bill summary",
            "activeVersion": "A",
            "basePrintNo": "S100",
            "billType": {'chamber': "SENATE"},
            "status": {
                "statusDesc": "In Committee",
            },
            "amendments": {
                "items": {
                    "A": {
                        "coSponsors": {
                            "items": [{
                                "memberId": 2,
                                "fullName": "Jabari"
                            }]
                        },
                        "sameAs": {
                            "items": [
                                {
                                    "basePrintNo": "A123",
                                    "billType": "ASSEMBLY"
                                }
                            ]
                        }
                    }
                }
            }
        }},
    )
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/2021/A123?view=no_fulltext&key=fake_key",
        json={"result": {
            "title": "Assembly bill title",
            "summary": "Assembly bill summary",
            "activeVersion": "",
            "basePrintNo": "A123",
            "billType": {'chamber': "ASSEMBLY"},
            "status": {
                "statusDesc": "Signed",
            },
            "amendments": {
                "items": {
                    "": {
                        "coSponsors": {
                            "items": [{
                                "memberId": 1,
                                "fullName": "Jabari"
                            }]
                        },
                    }
                }
            }
        }},
    )

    senate_non_sponsor = Person(
        name="Senate non sponsor", type=Person.PersonType.SENATOR
    )
    senate_non_sponsor.senator = Senator(state_member_id=5)
    senate_sponsor = Person(
        name="Senate sponsor", type=Person.PersonType.SENATOR
    )
    senate_sponsor.senator = Senator(state_member_id=2)
    db.session.add(senate_sponsor)

    assembly_non_sponsor = Person(
        name="Assembly non sponsor", type=Person.PersonType.ASSEMBLY_MEMBER
    )
    assembly_non_sponsor.assembly_member = AssemblyMember(state_member_id=50)
    assembly_sponsor = Person(
        name="Assembly sponsor", type=Person.PersonType.ASSEMBLY_MEMBER
    )
    assembly_sponsor.assembly_member = AssemblyMember(state_member_id=1)
    db.session.add(assembly_sponsor)

    db.session.commit()

    response = client.post(
        "/api/state-bills/track",
        data={"sessionYear": 2021, "basePrintNo": "S100"},
    )
    assert response.status_code == 200

    bill = Bill.query.one()
    assert bill.type == Bill.BillType.STATE
    assert bill.state_bill.session_year == 2021
    assert bill.state_bill.senate_bill.base_print_no == "S100"
    assert bill.state_bill.senate_bill.status == "In Committee"
    assert bill.state_bill.senate_bill.active_version == "A"
    assert bill.state_bill.assembly_bill.base_print_no == "A123"
    assert bill.state_bill.assembly_bill.status == "Signed"
    assert bill.state_bill.assembly_bill.active_version == ""

    assert len(bill.state_bill.senate_bill.sponsorships) == 1
    assert (
        bill.state_bill.senate_bill.sponsorships[0].senator.person.name == "Senate sponsor"
    )

    assert len(bill.state_bill.assembly_bill.sponsorships) == 1
    assert (
        bill.state_bill.assembly_bill.sponsorships[0].assembly_member.person.name == "Assembly sponsor"
    )


# TODO: Add test for importing a bill that already exists
# And for one that doesn't have a "same as"
# And for one that only recently got a "same as"


# @responses.activate
# def test_save_bill__already_exists(client):
#     bill = Bill(name="name", description="description", type=Bill.BillType.CITY)
#     bill.city_bill = CityBill(
#         city_bill_id=1,
#         file="file",
#         intro_date=now(),
#         status="Committee",
#         active_version="A",
#     )
#     db.session.add(bill)
#     db.session.commit()

#     response = client.post(
#         "/api/city-bills/track",
#         data={"cityBillId": 1},
#     )
#     assert response.status_code == 409

# Test that it filters resolutions too?


@responses.activate
def test_search_bill_not_tracked(client):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/search?term=%28basePrintNo%3ANone+OR+printNo%3ANone%29+AND+billType.resolution%3Afalse+AND+session%3A2021&key=fake_key",
        json={"result": {
            "items": [{
                "result": {
                    "title": "Bill title",
                    "summary": "Long bill summary",
                    "session": 2021,
                    "basePrintNo": "S123",
                    "activeVersion": "A",
                    "status": {
                        "statusDesc": "Committee"
                    },
                    "billType": {
                        "chamber": "SENATE"
                    }
                }
            }]
        }},
    )

    response = client.get(
        "/api/state-bills/search?sessionYear=2021&basePrintNo=S123",
    )
    assert response.status_code == 200
    response_data = json.loads(response.data)[0]
    assert response_data == {
        "name": "Bill title",
        "description": "Long bill summary",
        "status": "Committee",
        "chamber": "SENATE",
        "activeVersion": "A",
        "basePrintNo": "S123",
        "sessionYear": 2021,
        "tracked": False,
    }


# @responses.activate
# def test_lookup_bill_already_tracked(client):
#     bill = Bill(name="name", description="description", type=Bill.BillType.CITY)
#     bill.city_bill = CityBill(
#         city_bill_id=1,
#         file="file",
#         intro_date=now(),
#         status="Enacted",
#         active_version="A",
#     )
#     db.session.add(bill)
#     db.session.commit()

#     responses.add(
#         responses.GET,
#         url="https://webapi.legistar.com/v1/nyc/matters?token=fake_token&%24filter=MatterTypeName+eq+%27Introduction%27+and+substringof%28%271234%27%2C+MatterFile%29+eq+true",
#         json=[create_fake_matter(1)],
#     )

#     response = client.get(
#         "/api/city-bills/search?file=1234",
#     )
#     # assert more fields?
#     assert response.status_code == 200
#     response_data = json.loads(response.data)[0]
#     assert response_data["cityBill"]["cityBillId"] == 1
#     assert response_data["tracked"] == True
