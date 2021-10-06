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
                                    "userEnteredValue": {
                                        "stringValue": "SPONSORS"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                }
                            ]
                        },
                        {
                            "values": [
                                {
                                    "userEnteredValue": {
                                        "stringValue": "Name"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "Email"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "Party"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "District Phone"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "Legislative Phone"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "Twitter"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "Staffers"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "Notes"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                },
                            ]
                        },
                        {
                            "values": [
                                {
                                    "userEnteredValue": {
                                        "stringValue": "Sponsor"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                            ]
                        },
                        {"values": []},
                        {
                            "values": [
                                {
                                    "userEnteredValue": {
                                        "stringValue": "NON-SPONSORS"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": True}
                                    },
                                }
                            ]
                        },
                        {
                            "values": [
                                {
                                    "userEnteredValue": {
                                        "stringValue": "Non sponsor"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": "None"
                                    },
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                                {
                                    "userEnteredValue": {"stringValue": ""},
                                    "userEnteredFormat": {
                                        "textFormat": {"bold": False}
                                    },
                                },
                            ]
                        },
                    ]
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
