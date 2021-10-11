from __future__ import print_function

import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import joinedload, selectinload
from werkzeug import exceptions

from src import app, models, settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


class Cell:
    value = None  # str
    link_url = None  # str
    bold = False

    def __init__(self, value, *, link_url=None, bold=False):
        self.value = value
        self.link_url = link_url
        self.bold = bold


# TODO: Share this with TogglSync via a utils package?
def _get_google_credentials():
    # TODO: This will need to refresh the creds every time after first expiration? Maybe?
    creds = Credentials.from_authorized_user_info(
        json.loads(settings.GOOGLE_CREDENTIALS), SCOPES
    )
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise exceptions.InternalServerError(
                f"Creds were invalid but not refreshable: {settings.GOOGLE_CREDENTIALS}"
            )

    return creds


def _get_sheets_service(credentials):
    return build("sheets", "v4", credentials=credentials)


def _get_drive_service(credentials):
    return build("drive", "v3", credentials=credentials)


def _create_cell_data(cell):
    text_format_runs = None
    if cell.link_url:
        text_format_runs = [
            {"startIndex": 0, "format": {"link": {"uri": cell.link_url}}}
        ]
    return {
        "textFormatRuns": text_format_runs,
        "userEnteredValue": {"stringValue": str(cell.value)},
        "userEnteredFormat": {"textFormat": {"bold": cell.bold}},
    }


def _create_row_data(cells):
    return {"values": [_create_cell_data(cell) for cell in cells]}


def _create_legislator_row(legislator):
    staffer_strings = [s.display_string for s in legislator.staffers]
    staffer_text = "\n".join(staffer_strings)

    cells = [
        Cell(legislator.name),
        Cell(legislator.email),
        Cell(legislator.party),
        Cell(legislator.district_phone),
        Cell(legislator.legislative_phone),
        Cell(
            legislator.display_twitter or "", link_url=legislator.twitter_url
        ),
        Cell(staffer_text),
        Cell(legislator.notes or ""),
    ]
    return _create_row_data(cells)


def _create_title_row_data(raw_values):
    cells = [Cell(value, bold=True) for value in raw_values]
    return _create_row_data(cells)


def _create_phone_bank_spreadsheet_data(bill, sponsors, non_sponsors):
    """Generates the full body payload that the Sheets API requires for a
    phone bank spreadsheet."""
    rows = [
        _create_title_row_data(["SPONSORS"]),
        _create_title_row_data(
            [
                "Name",
                "Email",
                "Party",
                "District Phone",
                "Legislative Phone",
                "Twitter",
                "Staffers",
                "Notes",
            ],
        ),
    ]
    for sponsor in sponsors:
        rows.append(_create_legislator_row(sponsor))

    rows.append(_create_title_row_data([]))
    rows.append(_create_title_row_data(["NON-SPONSORS"]))

    for legislator in non_sponsors:
        rows.append(_create_legislator_row(legislator))

    return {
        "properties": {"title": f"Phone bank for {bill.file}"},
        "sheets": [{"data": {"rowData": rows}}],
    }


def create_phone_bank_spreadsheet(bill_id):
    """Creates a spreadsheet that's a template to run a phone bank
    for a specific bill, based on its current sponsors. The sheet will be
    owned by a robot Google account and will be made publicly editable by
    anyone with the link."""
    bill = (
        models.Bill.query.filter_by(id=bill_id)
        .options(
            selectinload(models.Bill.sponsorships),
            selectinload("sponsorships.legislator.staffers"),
        )
        .one()
    )

    sponsorships = bill.sponsorships
    sponsorships = sorted(sponsorships, key=lambda s: s.legislator.name)
    sponsors = [s.legislator for s in sponsorships]

    sponsor_ids = [s.legislator_id for s in sponsorships]
    non_sponsors = (
        models.Legislator.query.filter(
            models.Legislator.id.not_in(sponsor_ids)
        )
        .order_by(models.Legislator.name)
        .all()
    )

    spreadsheet_data = _create_phone_bank_spreadsheet_data(
        bill, sponsors, non_sponsors
    )

    google_credentials = _get_google_credentials()
    sheets_service = _get_sheets_service(google_credentials)

    spreadsheet_result = (
        sheets_service.spreadsheets().create(body=spreadsheet_data).execute()
    )

    # That sheet is initially only accessible to our robot account, so make it public.
    drive_service = _get_drive_service(google_credentials)
    user_permission = {
        "type": "anyone",
        "role": "writer",
    }
    drive_service.permissions().create(
        fileId=spreadsheet_result["spreadsheetId"],
        body=user_permission,
        fields="id",
    ).execute()

    return spreadsheet_result
