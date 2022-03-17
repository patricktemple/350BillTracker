from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.models import db
from src.person.models import (
    AssemblyMember,
    CouncilMember,
    OfficeContact,
    Person,
    Senator,
)
from src.power_hours import (
    CITY_COLUMN_TITLE_SET,
    _extract_data_from_previous_spreadsheet,
    create_power_hour,
)
from src.sponsorship.models import (
    AssemblySponsorship,
    CitySponsorship,
    SenateSponsorship,
)


@patch("src.google_sheets.Credentials")
@patch("src.google_sheets.build")
def test_create_city_power_hour__no_import(
    mock_build, mock_credentials, snapshot, city_bill
):
    mock_sheets_service = MagicMock()
    mock_drive_service = MagicMock()

    # TODO: Figure out how to reuse this as a fixture
    def side_effect(service, version, credentials=None):
        if service == "sheets":
            return mock_sheets_service
        if service == "drive":
            return mock_drive_service
        raise ValueError("wrong service")

    mock_build.side_effect = side_effect

    non_sponsor = Person(
        id=uuid4(), name="Non sponsor", type=Person.PersonType.COUNCIL_MEMBER
    )
    non_sponsor.council_member = CouncilMember(city_council_person_id=1)
    non_sponsor.office_contacts.append(
        OfficeContact(
            type=OfficeContact.OfficeContactType.CENTRAL_OFFICE,
            phone="111-222-3333",
        )
    )

    sponsor = Person(
        id=uuid4(), name="Sponsor", type=Person.PersonType.COUNCIL_MEMBER
    )
    sponsor.office_contacts.append(
        OfficeContact(
            type=OfficeContact.OfficeContactType.DISTRICT_OFFICE,
            phone="111-222-3333",
        )
    )
    sponsor.council_member = CouncilMember(city_council_person_id=2)
    db.session.add(sponsor)
    db.session.add(non_sponsor)

    db.session.add(
        CitySponsorship(
            council_member_id=sponsor.id,
            bill_id=city_bill.id,
            sponsor_sequence=0,
        )
    )
    db.session.commit()

    mock_sheets_service.spreadsheets().create().execute.return_value = {
        "spreadsheetId": "test_spreadsheet"
    }

    _, messages = create_power_hour(
        city_bill.id, title="My power hour", old_spreadsheet_to_import=None
    )
    assert messages == ["Spreadsheet was created"]

    mock_sheets_service.spreadsheets().create.assert_called_with(body=snapshot)
    mock_sheets_service.spreadsheets().create().execute.assert_called()

    mock_drive_service.permissions().create.assert_called_with(
        fileId="test_spreadsheet",
        fields="id",
        body={"type": "anyone", "role": "writer"},
    )


@patch("src.google_sheets.Credentials")
@patch("src.google_sheets.build")
def test_create_city_power_hour__with_import(
    mock_build, mock_credentials, snapshot, city_bill
):
    mock_sheets_service = MagicMock()
    mock_drive_service = MagicMock()

    # TODO: Share this setup in a fixture
    def side_effect(service, version, credentials=None):
        if service == "sheets":
            return mock_sheets_service
        if service == "drive":
            return mock_drive_service
        raise ValueError("wrong service")

    mock_build.side_effect = side_effect

    mock_sheets_service.spreadsheets.return_value.get.return_value.execute.return_value = {
        "sheets": [
            {
                "data": [
                    {
                        "rowData": [
                            {
                                "values": [
                                    {"formattedValue": "Name"},
                                    {"formattedValue": "Extra column"},
                                ]
                            },
                            {
                                "values": [
                                    {"formattedValue": "Brad Lander"},
                                    {"formattedValue": "Called"},
                                ]
                            },
                        ]
                    }
                ]
            }
        ]
    }

    non_sponsor = Person(
        id=uuid4(),
        name="Missing Person",
        type=Person.PersonType.COUNCIL_MEMBER,
    )
    non_sponsor.council_member = CouncilMember(city_council_person_id=1)
    sponsor = Person(
        id=uuid4(), name="Brad Lander", type=Person.PersonType.COUNCIL_MEMBER
    )
    sponsor.council_member = CouncilMember(city_council_person_id=2)
    db.session.add(sponsor)
    db.session.add(non_sponsor)

    db.session.add(
        CitySponsorship(
            council_member_id=sponsor.id,
            bill_id=city_bill.id,
            sponsor_sequence=0,
        )
    )
    db.session.commit()

    mock_sheets_service.spreadsheets().create().execute.return_value = {
        "spreadsheetId": "test_spreadsheet"
    }

    _, messages = create_power_hour(
        city_bill.id, title="My power hour", old_spreadsheet_to_import="123"
    )
    assert messages == [
        "Copied column 'Extra column' to new sheet",
        "Could not find Missing Person under the Name column in the old sheet. Make sure the name matches exactly.",
        "Spreadsheet was created",
    ]

    # TODO: Assert on the contents of the body that's passed in, not just the snapshot.
    # Needs a matcher.
    mock_sheets_service.spreadsheets().create.assert_called_with(body=snapshot)
    mock_sheets_service.spreadsheets().create().execute.assert_called()


@pytest.mark.parametrize(
    ("senate_bill_exists", "assembly_bill_exists"),
    [(False, True), (True, True), (True, False)],
)
@patch("src.google_sheets.Credentials")
@patch("src.google_sheets.build")
def test_create_state_power_hour__no_import(
    mock_build,
    mock_credentials,
    snapshot,
    state_bill,
    senator,
    assembly_member,
    senate_bill_exists,
    assembly_bill_exists,
):
    mock_sheets_service = MagicMock()
    mock_drive_service = MagicMock()

    # TODO: Figure out how to reuse this as a fixture
    def side_effect(service, version, credentials=None):
        if service == "sheets":
            return mock_sheets_service
        if service == "drive":
            return mock_drive_service
        raise ValueError("wrong service")

    mock_build.side_effect = side_effect

    if senate_bill_exists:
        non_sponsor_senator = Person(
            id=uuid4(),
            name="Non sponsor senator",
            type=Person.PersonType.SENATOR,
        )
        non_sponsor_senator.senator = Senator(state_member_id=1)
        non_sponsor_senator.office_contacts.append(
            OfficeContact(
                type=OfficeContact.OfficeContactType.CENTRAL_OFFICE,
                phone="111-222-3333",
                fax="123-567-1890",
                city="Albany",
            ),
        )
        db.session.add(non_sponsor_senator)

        # The sponsor is fully defined from the "senator" fixture already
        db.session.add(
            SenateSponsorship(
                person_id=senator.id,
                bill_id=state_bill.id,
                is_lead_sponsor=True,
            )
        )
    else:
        state_bill.senate_bill = None

    if assembly_bill_exists:
        non_sponsor_assembly_member = Person(
            id=uuid4(),
            name="Non sponsor assembly member",
            type=Person.PersonType.ASSEMBLY_MEMBER,
        )
        non_sponsor_assembly_member.assembly_member = AssemblyMember(
            state_member_id=2
        )
        non_sponsor_assembly_member.office_contacts.append(
            OfficeContact(
                type=OfficeContact.OfficeContactType.DISTRICT_OFFICE,
                phone="111-222-444",
                fax="123-567-800",
                city="Manhattan",
            ),
        )
        db.session.add(non_sponsor_assembly_member)
        db.session.add(
            AssemblySponsorship(
                person_id=assembly_member.id,
                bill_id=state_bill.id,
                is_lead_sponsor=False,
            )
        )
    else:
        state_bill.assembly_bill = None
    db.session.commit()

    mock_sheets_service.spreadsheets().create().execute.return_value = {
        "spreadsheetId": "test_spreadsheet"
    }

    _, messages = create_power_hour(
        state_bill.id, title="My power hour", old_spreadsheet_to_import=None
    )
    assert messages == ["Spreadsheet was created"]

    mock_sheets_service.spreadsheets().create.assert_called_with(body=snapshot)
    mock_sheets_service.spreadsheets().create().execute.assert_called()

    mock_drive_service.permissions().create.assert_called_with(
        fileId="test_spreadsheet",
        fields="id",
        body={"type": "anyone", "role": "writer"},
    )


@patch("src.google_sheets.Credentials")
@patch("src.google_sheets.build")
def test_create_state_power_hour__with_import(
    mock_build, mock_credentials, snapshot, state_bill, senator
):
    mock_sheets_service = MagicMock()
    mock_drive_service = MagicMock()

    # TODO: Figure out how to reuse this as a fixture
    def side_effect(service, version, credentials=None):
        if service == "sheets":
            return mock_sheets_service
        if service == "drive":
            return mock_drive_service
        raise ValueError("wrong service")

    mock_build.side_effect = side_effect

    mock_sheets_service.spreadsheets.return_value.get.return_value.execute.return_value = {
        "sheets": [
            {
                "data": [
                    {
                        "rowData": [
                            {
                                "values": [
                                    {"formattedValue": "Name"},
                                    {"formattedValue": "Extra column"},
                                ]
                            },
                            {
                                "values": [
                                    {"formattedValue": senator.name},
                                    {"formattedValue": "Called"},
                                ]
                            },
                        ]
                    }
                ]
            }
        ]
    }

    mock_sheets_service.spreadsheets().create().execute.return_value = {
        "spreadsheetId": "test_spreadsheet"
    }

    _, messages = create_power_hour(
        state_bill.id,
        title="My power hour",
        old_spreadsheet_to_import="old spreadsheet id",
    )
    assert messages == [
        "Copied column 'Extra column' to new sheet",
        "Spreadsheet was created",
    ]

    mock_sheets_service.spreadsheets().create.assert_called_with(body=snapshot)
    mock_sheets_service.spreadsheets().create().execute.assert_called()

    mock_drive_service.permissions().create.assert_called_with(
        fileId="test_spreadsheet",
        fields="id",
        body={"type": "anyone", "role": "writer"},
    )


def test_extract_data_from_previous_spreadsheet():
    corey = Person(
        name="Corey D. Johnson", type=Person.PersonType.COUNCIL_MEMBER
    )
    corey.council_member = CouncilMember(city_council_person_id=1)
    db.session.add(corey)

    retired = Person(
        name="Retired Person", type=Person.PersonType.COUNCIL_MEMBER
    )
    retired.council_member = CouncilMember(city_council_person_id=2)
    db.session.add(retired)

    lead = Person(name="Lead Sponsor", type=Person.PersonType.COUNCIL_MEMBER)
    lead.council_member = CouncilMember(city_council_person_id=3)
    db.session.add(lead)
    db.session.commit()

    cell_data = [
        ["Name", "Email", "Summary of action"],
        ["Corey D. Johnson", "cojo@council.ny.gov", "Left a voicemail"],
        ["Lead Sponsor (lead)", "lead@council.ny.gov", "Called them"],
        ["Bread Lender", "bread@council.ny.gov", "Put a typo in Brad's name"],
    ]

    result = _extract_data_from_previous_spreadsheet(
        cell_data, CITY_COLUMN_TITLE_SET, [Person.PersonType.COUNCIL_MEMBER]
    )

    assert result.extra_column_titles == ["Summary of action"]
    assert len(result.column_data_by_person_id) == 2
    assert (
        result.column_data_by_person_id[corey.id]["Summary of action"]
        == "Left a voicemail"
    )
    assert (
        result.column_data_by_person_id[lead.id]["Summary of action"]
        == "Called them"
    )
    assert result.import_messages == [
        "Copied column 'Summary of action' to new sheet",
        "Could not find Retired Person under the Name column in the old sheet. Make sure the name matches exactly.",
    ]


def test_extract_data_from_previous_spreadsheet_no_name():
    corey = Person(
        name="Corey D. Johnson", type=Person.PersonType.COUNCIL_MEMBER
    )
    corey.council_member = CouncilMember(city_council_person_id=1)
    db.session.add(corey)
    db.session.commit()

    cell_data = [
        ["Name typoed", "Email", "Summary of action"],
        ["Corey D. Johnson", "cojo@council.ny.gov", "Left a voicemail"],
    ]

    result = _extract_data_from_previous_spreadsheet(
        cell_data, CITY_COLUMN_TITLE_SET, [Person.PersonType.COUNCIL_MEMBER]
    )

    assert not result.column_data_by_person_id
    assert result.import_messages == [
        "Could not find a 'Name' column at the top of the old spreadsheet, so nothing was copied over"
    ]
