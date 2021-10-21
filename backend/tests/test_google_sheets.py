from unittest.mock import MagicMock, patch

from src import app
from src.google_sheets import create_phone_bank_spreadsheet
from src.models import Bill, BillSponsorship, Legislator, db
from src.utils import now


@patch("src.google_sheets.Credentials")
@patch("src.google_sheets.build")
def test_generate_google_sheet(mock_build, mock_credentials):
    mock_sheets_service = MagicMock()
    mock_drive_service = MagicMock()

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

    create_phone_bank_spreadsheet(1234)

    # TODO: Use a snapshot or something
    expected_data = {
        "properties": {"title": "Phone bank for Intro 3"},
        "sheets": [
            {
                "data": {
                    "rowData": [
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
                                        "stringValue": "Twitter search\nNote: Note: Due to a Twitter bug, the Twitter search sometimes displays 0 results even when there should be should be matching tweets. Refreshing the Twitter page often fixes this."
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
                        {"pixelSize": 200},
                        {"pixelSize": 100},
                        {"pixelSize": 100},
                        {"pixelSize": 150},
                        {"pixelSize": 200},
                        {"pixelSize": 250},
                        {"pixelSize": 250},
                    ],
                }
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
