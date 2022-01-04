import json
from uuid import uuid4

import pytest
import responses

from src.bill.models import (
    DEFAULT_TWITTER_SEARCH_TERMS,
    AssemblyBill,
    Bill,
    SenateBill,
    StateBill,
)
from src.models import db
from src.person.models import AssemblyMember, Person, Senator
from src.utils import now

from .utils import assert_response


def test_get_bills(client, state_bill):
    response = client.get("/api/bills")
    assert_response(
        response,
        200,
        [
            {
                "cityBill": None,
                "codeName": "S1234 / A1234 from 2021 session",
                "description": "description",
                "id": str(state_bill.id),
                "name": "state bill",
                "nickname": "nickname",
                "notes": "",
                "stateBill": {
                    "assemblyBill": {
                        "activeVersion": "A",
                        "assemblyWebsite": "https://nyassembly.gov/leg/?term=2021&bn=A1234",
                        "basePrintNo": "A1234",
                        "senateWebsite": "https://www.nysenate.gov/legislation/bills/2021/A1234",
                        "sponsorCount": 0,
                        "status": "Voted",
                    },
                    "senateBill": {
                        "activeVersion": "",
                        "assemblyWebsite": "https://nyassembly.gov/leg/?term=2021&bn=S1234",
                        "basePrintNo": "S1234",
                        "senateWebsite": "https://www.nysenate.gov/legislation/bills/2021/S1234",
                        "sponsorCount": 0,
                        "status": "Committee",
                    },
                },
                "status": "Committee / Voted",
                "tracked": True,
                "twitterSearchTerms": [
                    "solar",
                    "climate",
                    "wind power",
                    "renewable",
                    "fossil fuel",
                ],
                "type": "STATE",
            }
        ],
    )


def test_delete_bill(client, state_bill):
    response = client.get("/api/bills")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1

    response = client.delete(f"/api/bills/{state_bill.id}")
    assert response.status_code == 200

    response = client.get("/api/bills")
    assert_response(response, 200, [])


def create_mock_bill_response(
    *,
    base_print_no,
    chamber,
    cosponsor_member_id,
    same_as_base_print_no=None,
    same_as_chamber=None,
):
    return {
        "result": {
            "title": f"{base_print_no} bill title",
            "summary": f"{base_print_no} bill summary",
            "activeVersion": "A",
            "basePrintNo": base_print_no,
            "billType": {"chamber": chamber},
            "status": {
                "statusDesc": "In Committee",
            },
            "amendments": {
                "items": {
                    "A": {
                        "coSponsors": {
                            "items": [
                                {
                                    "memberId": cosponsor_member_id,
                                    "fullName": "Jabari",
                                }
                            ]
                        },
                        "sameAs": {
                            "items": None
                            if not same_as_base_print_no
                            else [
                                {
                                    "basePrintNo": same_as_base_print_no,
                                    "billType": {"chamber": same_as_chamber},
                                }
                            ]
                        },
                    }
                }
            },
        }
    }


@responses.activate
def test_track_bill(client):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/2021/S100?view=no_fulltext&key=fake_key",
        json=create_mock_bill_response(
            base_print_no="S100",
            chamber="SENATE",
            same_as_chamber="ASSEMBLY",
            same_as_base_print_no="A123",
            cosponsor_member_id=2,
        ),
    )
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/2021/A123?view=no_fulltext&key=fake_key",
        json=create_mock_bill_response(
            base_print_no="A123", chamber="ASSEMBLY", cosponsor_member_id=1
        ),
    )

    senate_non_sponsor = Person(
        name="Senate non sponsor", type=Person.PersonType.SENATOR
    )
    senate_non_sponsor.senator = Senator(state_member_id=5)
    db.session.add(senate_non_sponsor)

    senate_sponsor = Person(
        name="Senate sponsor", type=Person.PersonType.SENATOR
    )
    senate_sponsor.senator = Senator(state_member_id=2)
    db.session.add(senate_sponsor)

    assembly_non_sponsor = Person(
        name="Assembly non sponsor", type=Person.PersonType.ASSEMBLY_MEMBER
    )
    assembly_non_sponsor.assembly_member = AssemblyMember(state_member_id=50)
    db.session.add(assembly_non_sponsor)

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
    assert bill.state_bill.assembly_bill.status == "In Committee"
    assert bill.state_bill.assembly_bill.active_version == "A"

    assert len(bill.state_bill.senate_bill.sponsorships) == 1
    assert (
        bill.state_bill.senate_bill.sponsorships[0].senator.person.name
        == "Senate sponsor"
    )

    assert len(bill.state_bill.assembly_bill.sponsorships) == 1
    assert (
        bill.state_bill.assembly_bill.sponsorships[
            0
        ].assembly_member.person.name
        == "Assembly sponsor"
    )


@responses.activate
def test_track_bill__senate_only(client):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/2021/S100?view=no_fulltext&key=fake_key",
        json=create_mock_bill_response(
            base_print_no="S100", chamber="SENATE", cosponsor_member_id=2
        ),
    )

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
    assert bill.state_bill.assembly_bill is None


@responses.activate
def test_track_bill__assembly_only(client):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/2021/A100?view=no_fulltext&key=fake_key",
        json=create_mock_bill_response(
            base_print_no="A100", chamber="ASSEMBLY", cosponsor_member_id=2
        ),
    )

    db.session.commit()

    response = client.post(
        "/api/state-bills/track",
        data={"sessionYear": 2021, "basePrintNo": "A100"},
    )
    assert response.status_code == 200

    bill = Bill.query.one()
    assert bill.type == Bill.BillType.STATE
    assert bill.state_bill.session_year == 2021
    assert bill.state_bill.assembly_bill.base_print_no == "A100"
    assert bill.state_bill.assembly_bill.status == "In Committee"
    assert bill.state_bill.assembly_bill.active_version == "A"
    assert bill.state_bill.senate_bill is None


@responses.activate
def test_track_bill__senate_already_exists(client):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/2021/S100?view=no_fulltext&key=fake_key",
        json=create_mock_bill_response(
            base_print_no="S100", chamber="SENATE", cosponsor_member_id=2
        ),
    )

    bill = Bill(
        id=uuid4(),
        name="state bill",
        description="description",
        nickname="nickname",
        type=Bill.BillType.STATE,
    )
    bill.state_bill = StateBill(
        session_year=2021,
    )
    bill.state_bill.senate_bill = SenateBill(
        base_print_no="S100", active_version="", status="Committee"
    )
    db.session.add(bill)
    db.session.commit()

    response = client.post(
        "/api/state-bills/track",
        data={"sessionYear": 2021, "basePrintNo": "S100"},
    )
    assert response.status_code == 409


@responses.activate
def test_track_bill__assembly_already_exists(client):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/2021/A100?view=no_fulltext&key=fake_key",
        json=create_mock_bill_response(
            base_print_no="A100", chamber="ASSEMBLY", cosponsor_member_id=2
        ),
    )

    bill = Bill(
        id=uuid4(),
        name="state bill",
        description="description",
        nickname="nickname",
        type=Bill.BillType.STATE,
    )
    bill.state_bill = StateBill(
        session_year=2021,
    )
    bill.state_bill.assembly_bill = AssemblyBill(
        base_print_no="A100", active_version="", status="Committee"
    )
    db.session.add(bill)
    db.session.commit()

    response = client.post(
        "/api/state-bills/track",
        data={"sessionYear": 2021, "basePrintNo": "A100"},
    )
    assert response.status_code == 409


@responses.activate
@pytest.mark.parametrize("tracked", [False, True])
def test_search_bill(client, tracked):
    responses.add(
        responses.GET,
        url="https://legislation.nysenate.gov/api/3/bills/search?term=%28basePrintNo%3AS123+OR+printNo%3AS123%29+AND+billType.resolution%3Afalse+AND+session%3A2021&key=fake_key",
        json={
            "result": {
                "items": [
                    {
                        "result": {
                            "title": "Bill title",
                            "summary": "Long bill summary",
                            "session": 2021,
                            "basePrintNo": "S123",
                            "activeVersion": "A",
                            "status": {"statusDesc": "Committee"},
                            "billType": {"chamber": "SENATE"},
                        }
                    }
                ]
            }
        },
    )

    if tracked:
        bill = Bill(
            id=uuid4(),
            name="state bill",
            description="description",
            nickname="nickname",
            type=Bill.BillType.STATE,
        )
        bill.state_bill = StateBill(
            session_year=2021,
        )
        bill.state_bill.senate_bill = SenateBill(
            base_print_no="S123", active_version="", status="Committee"
        )
        db.session.add(bill)
        db.session.commit()

    response = client.get(
        "/api/state-bills/search?sessionYear=2021&codeName=S123",
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
        "tracked": tracked,
    }
