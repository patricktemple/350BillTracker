import json
from re import L
from unittest.mock import MagicMock, patch

import pytest

from src import app
from src.google_sheets import (
    _extract_data_from_previous_power_hour,
    _extract_data_from_previous_spreadsheet,
    create_power_hour,
)
from src.models import Bill, BillSponsorship, Legislator, PowerHour, db
from src.utils import now


@patch("src.google_sheets.Credentials")
@patch("src.google_sheets.build")
def test_generate_google_sheet__no_import(mock_build, mock_credentials):
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

    bill = Bill(
        id=1234,
        file="Intro 3",
        name="Ban oil",
        title="Ban all oil",
        intro_date=now(),
    )
    db.session.add(bill)

    non_sponsor = Legislator(id=1, name="Non sponsor")
    sponsor = Legislator(id=2, name="Sponsor")
    db.session.add(sponsor)
    db.session.add(non_sponsor)

    db.session.add(BillSponsorship(legislator_id=sponsor.id, bill_id=bill.id))
    db.session.commit()

    mock_sheets_service.spreadsheets().create().execute.return_value = {
        "spreadsheetId": "test_spreadsheet"
    }

    _, messages = create_power_hour(
        1234, title="My power hour", old_spreadsheet_to_import=None
    )
    assert messages == ["Spreadsheet was created"]

    # TODO: Use a snapshot or something
    expected_data = {
        "properties": {"title": "My power hour"},
        "sheets": [
            {
                "properties": {"gridProperties": {"frozenRowCount": 1}},
                "data": {
                    "rowData": [
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Name"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Email"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Party"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Borough"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "District Phone"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Legislative Phone"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Twitter"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Twitter search\nNote: Due to a Twitter bug, the Twitter search sometimes displays 0 results even when there should be should be matching tweets. Refreshing the Twitter page often fixes this."
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Staffers"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Notes"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                            ]
                        },
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "NON-SPONSORS"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                }
                            ]
                        },
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Non sponsor"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                            ]
                        },
                        {"values": []},
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "SPONSORS"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                }
                            ]
                        },
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Sponsor"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                            ]
                        },
                    ],
                    "columnMetadata": [
                        {"pixelSize": 150},
                        {"pixelSize": 150},
                        {"pixelSize": 200},
                        {"pixelSize": 50},
                        {"pixelSize": 100},
                        {"pixelSize": 100},
                        {"pixelSize": 150},
                        {"pixelSize": 200},
                        {"pixelSize": 250},
                        {"pixelSize": 250},
                    ],
                },
            }
        ],
    }
    mock_sheets_service.spreadsheets().create.assert_called_with(
        body=expected_data
    )
    mock_sheets_service.spreadsheets().create().execute.assert_called()

    mock_drive_service.permissions().create.assert_called_with(
        fileId="test_spreadsheet",
        fields="id",
        body={"type": "anyone", "role": "writer"},
    )


@patch("src.google_sheets.Credentials")
@patch("src.google_sheets.build")
def test_generate_google_sheet__with_import(mock_build, mock_credentials):
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

    bill = Bill(
        id=1234,
        file="Intro 3",
        name="Ban oil",
        title="Ban all oil",
        intro_date=now(),
    )
    db.session.add(bill)

    non_sponsor = Legislator(id=1, name="Missing Person")
    sponsor = Legislator(id=2, name="Brad Lander")
    db.session.add(sponsor)
    db.session.add(non_sponsor)

    db.session.add(BillSponsorship(legislator_id=sponsor.id, bill_id=bill.id))
    db.session.commit()

    mock_sheets_service.spreadsheets().create().execute.return_value = {
        "spreadsheetId": "test_spreadsheet"
    }

    _, messages = create_power_hour(
        1234, title="My power hour", old_spreadsheet_to_import="123"
    )
    assert messages == [
        "Copied column 'Extra column' to new sheet",
        "Could not find Missing Person under the Name column in the old sheet. Make sure the name matches exactly.",
        "Spreadsheet was created",
    ]

    # TODO: Use a snapshot or something
    expected_data = {
        "properties": {"title": "My power hour"},
        "sheets": [
            {
                "properties": {"gridProperties": {"frozenRowCount": 1}},
                "data": {
                    "rowData": [
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Name"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Email"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Party"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Borough"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "District Phone"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Legislative Phone"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Twitter"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Twitter search\nNote: Due to a Twitter bug, the Twitter search sometimes displays 0 results even when there should be should be matching tweets. Refreshing the Twitter page often fixes this."
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Staffers"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Notes"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Extra column"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                },
                            ]
                        },
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "NON-SPONSORS"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                }
                            ]
                        },
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Missing Person"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                            ]
                        },
                        {"values": []},
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "SPONSORS"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": True},
                                    },
                                }
                            ]
                        },
                        {
                            "values": [
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Brad Lander"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                                {
                                    "textFormatRuns": None,
                                    "userEnteredValue": {
                                        "stringValue": "Called"
                                    },
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "textFormat": {"bold": False},
                                    },
                                },
                            ]
                        },
                    ],
                    "columnMetadata": [
                        {"pixelSize": 150},
                        {"pixelSize": 150},
                        {"pixelSize": 200},
                        {"pixelSize": 50},
                        {"pixelSize": 100},
                        {"pixelSize": 100},
                        {"pixelSize": 150},
                        {"pixelSize": 200},
                        {"pixelSize": 250},
                        {"pixelSize": 250},
                    ],
                },
            }
        ],
    }
    assert "Called" in json.dumps(
        expected_data
    )  # SUPER dumb to assert on this, use a matcher
    assert "Extra column" in json.dumps(expected_data)
    mock_sheets_service.spreadsheets().create.assert_called_with(
        body=expected_data
    )
    mock_sheets_service.spreadsheets().create().execute.assert_called()


@patch("src.google_sheets.Credentials")
@patch("src.google_sheets.build")
def test_extract_data_from_previous_power_hour(mock_build, mock_credentials):
    mock_sheets_service = MagicMock()

    mock_build.return_value = mock_sheets_service
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

    result = _extract_data_from_previous_power_hour("abc")
    print(result)


def test_extract_data_from_previous_spreadsheet():
    corey = Legislator(id=1, name="Corey D. Johnson")
    db.session.add(corey)

    retired = Legislator(id=2, name="Retired Person")
    db.session.add(retired)

    lead = Legislator(id=3, name="Lead Sponsor")
    db.session.add(lead)
    db.session.commit()

    cell_data = [
        ["Name", "Email", "Summary of action"],
        ["Corey D. Johnson", "cojo@council.ny.gov", "Left a voicemail"],
        ["Lead Sponsor (lead)", "lead@council.ny.gov", "Called them"],
        ["Bread Lender", "bread@council.ny.gov", "Put a typo in Brad's name"],
    ]

    result = _extract_data_from_previous_spreadsheet(cell_data)

    assert result.extra_column_titles == ["Summary of action"]
    assert len(result.column_data_by_legislator_id) == 2
    assert (
        result.column_data_by_legislator_id[corey.id]["Summary of action"]
        == "Left a voicemail"
    )
    assert (
        result.column_data_by_legislator_id[lead.id]["Summary of action"]
        == "Called them"
    )
    assert result.import_messages == [
        "Copied column 'Summary of action' to new sheet",
        "Could not find Retired Person under the Name column in the old sheet. Make sure the name matches exactly.",
    ]


def test_extract_data_from_previous_spreadsheet_no_name():
    corey = Legislator(id=1, name="Corey D. Johnson")
    db.session.add(corey)
    db.session.commit()

    cell_data = [
        ["Name typoed", "Email", "Summary of action"],
        ["Corey D. Johnson", "cojo@council.ny.gov", "Left a voicemail"],
    ]

    result = _extract_data_from_previous_spreadsheet(cell_data)

    assert not result.column_data_by_legislator_id
    assert result.import_messages == [
        "Could not find a 'Name' column at the top of the old spreadsheet, so nothing was copied over"
    ]
